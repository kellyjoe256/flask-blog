from flask import (Blueprint, jsonify, abort)
from app.models import Post, User

api = Blueprint('api', __name__)


@api.route('/')
@api.route('/posts')
def posts():
    entities = (Post.post_id, Post.title, Post.content_html,
                Post.created_at, User.name.label('author'))
    posts = Post.query.with_entities(*entities).join(User). \
        filter(Post.published == 1). \
        order_by(Post.created_at.desc()). \
        limit(10). \
        all()
    formatted_posts_for_json = []
    for post in posts:
        temp = {
            'post_id': post.post_id,
            'title': post.title,
            'body': post.content_html,
            'created_on': post.created_at.strftime('%B %d, %Y'),
            'author': post.author,
        }
        formatted_posts_for_json.append(temp)
    return jsonify(formatted_posts_for_json)


@api.route('/post/<int:post_id>')
def post(post_id):
    entities = (Post.post_id, Post.title, Post.content_html,
                Post.created_at, User.name.label('author'))
    post = Post.query.with_entities(*entities).join(User). \
        filter(Post.published == 1). \
        filter(Post.post_id == post_id) . \
        first()
    formatted_post_for_json = {}
    if post:
        formatted_post_for_json = {
            'post_id': post.post_id,
            'title': post.title,
            'body': post.content_html,
            'created_on': post.created_at.strftime('%B %d, %Y'),
            'author': post.author,
        }
    return jsonify(formatted_post_for_json)


@api.route('/author/<username>')
def author_posts(username):
    entities = (User.user_id, User.username, User.name)
    user = User.query.with_entities(*entities). \
        filter(User.username == username).first()
    if not user:
        abort(404)
    entities = (Post.post_id, Post.title, Post.created_at,
                Post.content_html, User.name.label('author'))
    posts = Post.query.with_entities(*entities).join(User). \
        filter(User.user_id == user.user_id). \
        filter(Post.published == 1). \
        order_by(Post.created_at.desc()). \
        limit(10). \
        all()
    formatted_posts_for_json = []
    for post in posts:
        temp = {
            'post_id': post.post_id,
            'title': post.title,
            'body': post.content_html,
            'created_on': post.created_at.strftime('%B %d, %Y'),
            'author': post.author,
        }
        formatted_posts_for_json.append(temp)
    return jsonify(formatted_posts_for_json)
