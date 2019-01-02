from time import strptime
from sqlalchemy import cast, extract, Boolean
from flask import (Blueprint, render_template, request, current_app, abort)
from app.models import Post, User, Tag

main = Blueprint('main', __name__)


@main.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    entities = (Post.title, Post.created_at, Post.slug, Post.cover_image,
                User.username, User.name.label('author'))
    pagination = Post.query.with_entities(*entities).join(User). \
        filter(cast(Post.published, Boolean) == bool(1)). \
        order_by(Post.created_at.desc()). \
        paginate(page,
                 per_page=current_app.config.get('PER_PAGE', 10),
                 error_out=False)
    posts = pagination.items
    data = {
        'title': 'Blog',
        'posts': posts,
        'pagination': pagination,
        'archives': Post.get_archives(),
        'recent_posts': Post.get_recent_posts(),
    }
    return render_template('main/index.html', **data)


@main.route('/<slug>')
def show_post(slug):
    entities = (Post.post_id, Post.title, Post.created_at,
                Post.cover_image, Post.content_html,
                User.username, User.name.label('author'))
    post = Post.query.with_entities(*entities).join(User). \
        filter(cast(Post.published, Boolean) == bool(1)). \
        filter(Post.slug == slug).first()
    if not post:
        abort(404)
    tags = Tag.query.join(Post.tags).filter(Post.post_id == post.post_id).all()
    data = {
        'title': post.title,
        'post': post,
        'post_tags': tags,
        'archives': Post.get_archives(),
        'recent_posts': Post.get_recent_posts(),
    }
    return render_template('main/show.html', **data)


@main.route('/author/<username>')
def show_user_posts(username):
    entities = (User.user_id, User.username, User.name)
    user = User.query.with_entities(*entities). \
        filter(User.username == username).first()
    if not user:
        abort(404)
    page = request.args.get('page', 1, type=int)
    entities = (Post.post_id, Post.title, Post.created_at, Post.slug,
                Post.cover_image, Post.content_html,
                User.username, User.name.label('author'))
    pagination = Post.query.with_entities(*entities).join(User). \
        filter(User.user_id == user.user_id). \
        filter(cast(Post.published, Boolean) == bool(1)). \
        order_by(Post.created_at.desc()). \
        paginate(page,
                 per_page=current_app.config.get('PER_PAGE', 10),
                 error_out=False)
    posts = pagination.items
    data = {
        'title': '"' + user.name + '" Posts',
        'user': user,
        'posts': posts,
        'pagination': pagination,
        'archives': Post.get_archives(),
        'recent_posts': Post.get_recent_posts(),
    }
    return render_template('main/author_posts.html', **data)


@main.route('/tag/<slug>')
def show_tag_posts(slug):
    entities = (Tag.tag_id, Tag.name)
    tag = Tag.query.with_entities(*entities). \
        filter(Tag.slug == slug).first()
    if not tag:
        abort(404)
    page = request.args.get('page', 1, type=int)
    entities = (Post.post_id, Post.title, Post.created_at, Post.slug,
                Post.cover_image, Post.content_html,
                User.username, User.name.label('author'))
    pagination = Post.query.with_entities(*entities). \
        join(User).join(Post.tags). \
        filter(Tag.tag_id == tag.tag_id). \
        filter(cast(Post.published, Boolean) == bool(1)). \
        order_by(Post.created_at.desc()). \
        paginate(page,
                 per_page=current_app.config.get('PER_PAGE', 10),
                 error_out=False)
    posts = pagination.items
    data = {
        'title': '"' + tag.name + '" Posts',
        'tag': tag,
        'tag_posts': posts,
        'pagination': pagination,
        'archives': Post.get_archives(),
        'recent_posts': Post.get_recent_posts(),
    }
    return render_template('main/tag_posts.html', **data)


@main.route('/archives/<month>/<int:year>')
def show_archive_posts(month, year):
    numeric_month = strptime(month, '%B').tm_mon or 1
    page = request.args.get('page', 1, type=int)
    entities = (Post.post_id, Post.title, Post.created_at, Post.slug,
                Post.cover_image, Post.content_html,
                User.username, User.name.label('author'))
    pagination = Post.query.with_entities(*entities).join(User). \
        filter(extract('month', Post.created_at) == numeric_month). \
        filter(extract('year', Post.created_at) == year). \
        filter(cast(Post.published, Boolean) == bool(1)). \
        order_by(Post.created_at.desc()). \
        paginate(page,
                 per_page=current_app.config.get('PER_PAGE', 10),
                 error_out=False)
    posts = pagination.items
    data = {
        'title': '"' + month + ' ' + str(year) + '" Posts',
        'posts': posts,
        'pagination': pagination,
        'archives': Post.get_archives(),
        'recent_posts': Post.get_recent_posts(),
    }
    return render_template('main/archived_posts.html', **data)
