import os
from flask import (Blueprint, render_template, request,
                   redirect, url_for, flash, current_app, abort)
from flask_login import login_required, current_user
from app import db, uploads
from app.utils import admin_required, append_timestamp
from app.admin.forms import (TagForm, ChangePasswordForm, PostForm,
                             AdminChangePasswordForm)
from app.models import Post, Tag, User

admin = Blueprint('admin', __name__)


def check_tag(tag_id):
    return Tag.query.filter(Tag.tag_id == tag_id).first()


def remove_tags(post_id):
    post = Post.query.get_or_404(post_id)
    post.tags = []
    db.session.commit()


@admin.route('/')
@admin.route('/dashboard')
@login_required
def dashboard():
    if current_user.is_admin:
        posts_count = Post.query.count()
        tags_count = Tag.query.count()
        users_count = User.query.count()
    else:
        posts_count = Post.query.filter(
            Post.user_id == current_user.user_id).count()

    data = {
        'title': 'Dashboard',
        'posts_count': posts_count,
    }
    if current_user.is_admin:
        data['tags_count'] = tags_count
        data['users_count'] = users_count
    return render_template('admin/index.html', **data)


@admin.route('/posts')
@login_required
def list_posts():
    page = request.args.get('page', 1, type=int)
    entities = (Post.post_id, Post.title, Post.published,
                Post.created_at, Post.updated_at)
    if current_user.is_admin:
        entities += (User.username, User.name.label('author'))
        pagination = Post.query.with_entities(*entities).join(User). \
            order_by(Post.created_at.desc()). \
            paginate(page,
                     per_page=current_app.config.get('PER_PAGE', 10),
                     error_out=False)
    else:
        pagination = Post.query.with_entities(*entities). \
            filter_by(user_id=current_user.user_id).\
            order_by(Post.created_at.desc()). \
            paginate(page,
                     per_page=current_app.config.get('PER_PAGE', 10),
                     error_out=False)
    posts = pagination.items
    data = {
        'title': 'Posts',
        'posts': posts,
        'pagination': pagination,
    }
    return render_template('admin/posts/index.html', **data)


@admin.route('/posts/create', methods=['GET', 'POST'])
@login_required
def create_post():
    form = PostForm(form=request.form)
    if request.method == 'POST' and form.validate():
        publish = False
        filename = None
        if form.publish.data:
            publish = True
        if 'cover_image' in request.files:
            cover_image = request.files['cover_image']
            image_name = cover_image.filename
            image_name_parts = image_name.split('.')
            image_name = append_timestamp(
                image_name_parts[0]) + '.' + image_name_parts[1]
            filename = uploads.save(cover_image, name=image_name)
        post = Post()
        post.post_title = form.title.data
        post.content = form.content.data
        post.user_id = current_user.user_id
        post.published = publish
        if filename:
            post.cover_image = filename
        tags = form.tags.data
        for tag_id in tags:
            tag = check_tag(tag_id)
            if tag:
                post.tags.append(tag)
        db.session.add(post)
        db.session.commit()

        flash('Post created successfully', 'success')
        return redirect(url_for('admin.list_posts'))

    data = {
        'title': 'Create Post',
        'form': form,
    }
    return render_template('admin/posts/create.html', **data)


@admin.route('/posts/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    if not (current_user.is_admin or
            int(post.user_id) == int(current_user.user_id)):
        abort(403)
    form = PostForm(form=request.form)
    post_tags = post.tags
    if request.method == 'POST' and form.validate():
        publish = False
        filename = None
        if form.publish.data:
            publish = True
        if 'cover_image' in request.files:
            cover_image = request.files['cover_image']
            image_name = cover_image.filename
            image_name_parts = image_name.split('.')
            image_name = append_timestamp(
                image_name_parts[0]) + '.' + image_name_parts[1]
            filename = uploads.save(cover_image, name=image_name)
        if post.title != form.title.data:
            post.post_title = form.title.data
        post.content = form.content.data
        post.published = publish
        if filename:
            # Remove previous image file, to save space
            if post.cover_image:
                upload_dir = current_app.config.get('UPLOAD_DIR', '')
                os.unlink(os.path.join(upload_dir, post.cover_image))
            post.cover_image = filename
        # remove previous tags
        remove_tags(post_id)
        # add new tags
        tags = form.tags.data
        for tag_id in tags:
            tag = check_tag(tag_id)
            if tag:
                post.tags.append(tag)
        db.session.add(post)
        db.session.commit()

        flash('Post edited successfully', 'success')
        return redirect(url_for('admin.list_posts'))

    form.title.data = post.title
    form.tags.data = [tag.tag_id for tag in post_tags]
    form.content.data = post.content
    form.publish.data = bool(post.published)
    data = {
        'title': 'Edit Post',
        'form': form,
        'post': post,
    }
    return render_template('admin/posts/edit.html', **data)


@admin.route('/posts/<int:post_id>/delete', methods=['GET', 'POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if not (current_user.is_admin or
            int(post.user_id) == int(current_user.user_id)):
        abort(403)
    if request.method == 'POST':
        submit_value = request.form.get('submit', 'Cancel')
        if submit_value == 'Delete Post':
            # Remove image file, if it exists
            if post.cover_image:
                upload_dir = current_app.config.get('UPLOAD_DIR', '')
                os.unlink(os.path.join(upload_dir, post.cover_image))
            # remove tags related to post
            remove_tags(post_id)

            db.session.delete(post)
            db.session.commit()

            flash('Post deleted successfully', 'success')
        return redirect(url_for('admin.list_posts'))

    data = {
        'title': 'Delete Post',
        'post': post,
    }
    return render_template('admin/posts/delete.html', **data)


@admin.route('/tags')
@login_required
def list_tags():
    page = request.args.get('page', 1, type=int)
    pagination = Tag.query.with_entities(Tag.tag_id, Tag.name).\
        order_by(Tag.name).paginate(page,
                                    per_page=current_app.config.
                                    get('PER_PAGE', 10),
                                    error_out=False)
    tags = pagination.items
    data = {
        'title': 'Tags',
        'tags': tags,
        'pagination': pagination,
    }
    return render_template('admin/tags/index.html', **data)


@admin.route('/tags/add', methods=['GET', 'POST'])
@login_required
def add_tag():
    form = TagForm(tag=None, form=request.form)
    if request.method == 'POST' and form.validate():
        tag = Tag()
        tag.name = form.name.data

        db.session.add(tag)
        db.session.commit()

        flash('Tag added successfully', 'success')
        return redirect(url_for('admin.list_tags'))

    data = {
        'title': 'Add Tag',
        'form': form,
    }
    return render_template('admin/tags/add.html', **data)


@admin.route('/tags/<int:tag_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_tag(tag_id):
    tag = Tag.query.get_or_404(tag_id)
    form = TagForm(tag=tag, form=request.form)
    if request.method == 'POST' and form.validate():
        tag.name = form.name.data

        db.session.add(tag)
        db.session.commit()

        flash('Tag edited successfully', 'success')
        return redirect(url_for('admin.list_tags'))

    data = {
        'title': 'Edit Tag',
        'form': form,
        'tag': tag,
    }
    return render_template('admin/tags/edit.html', **data)


@admin.route('/tags/<int:tag_id>/delete', methods=['GET', 'POST'])
@login_required
@admin_required
def delete_tag(tag_id):
    tag = Tag.query.get_or_404(tag_id)
    if request.method == 'POST':
        submit_value = request.form.get('submit', 'Cancel')
        if submit_value == 'Delete Tag':
            db.session.delete(tag)
            db.session.commit()

            flash('Tag deleted successfully', 'success')

        return redirect(url_for('admin.list_tags'))

    data = {
        'title': 'Delete Tag',
        'tag': tag,
    }
    return render_template('admin/tags/delete.html', **data)


@admin.route('/users')
@login_required
@admin_required
def list_users():
    page = request.args.get('page', 1, type=int)
    entities = (User.user_id, User.username, User.email, User.is_admin,
                User.active, User.created_at)
    pagination = User.query.with_entities(*entities).\
        order_by(User.username, User.created_at.desc()).\
        paginate(page,
                 per_page=current_app.config.get('PER_PAGE', 10),
                 error_out=False)
    users = pagination.items
    data = {
        'title': 'Users',
        'users': users,
        'pagination': pagination,
    }
    return render_template('admin/users/index.html', **data)


@admin.route('/users/<int:user_id>/activate')
@login_required
@admin_required
def activate_account(user_id):
    user = User.query.get_or_404(user_id)
    user.active = 1

    db.session.add(user)
    db.session.commit()

    flash('User account activated successfully', 'success')
    return redirect(url_for('admin.list_users'))


@admin.route('/users/<int:user_id>/deactivate')
@login_required
@admin_required
def deactivate_account(user_id):
    user = User.query.get_or_404(user_id)
    user.active = 0

    db.session.add(user)
    db.session.commit()

    flash('User account deactivated successfully', 'success')
    return redirect(url_for('admin.list_users'))


@admin.route('/users/<int:user_id>/make_admin')
@login_required
@admin_required
def make_admin(user_id):
    user = User.query.get_or_404(user_id)
    user.is_admin = 1

    db.session.add(user)
    db.session.commit()

    flash('User account is now an admin account', 'success')
    return redirect(url_for('admin.list_users'))


@admin.route('/users/<int:user_id>/revoke')
@login_required
@admin_required
def revoke_admin(user_id):
    user = User.query.get_or_404(user_id)
    user.is_admin = 0

    db.session.add(user)
    db.session.commit()

    redirect_to = url_for('admin.list_users')
    if current_user.user_id == user.user_id:
        redirect_to = url_for('admin.dashboard')

    flash('User account admin privileges removed', 'success')
    return redirect(redirect_to)


@admin.route('/users/<int:user_id>/change_user_password',
             methods=['GET', 'POST'])
@login_required
@admin_required
def change_user_password(user_id):
    user = User.query.get_or_404(user_id)
    form = AdminChangePasswordForm(form=request.form)
    if request.method == 'POST' and form.validate():
        user.password = form.password.data

        db.session.add(user)
        db.session.commit()

        flash('User password changed successfully', 'success')
        return redirect(url_for('admin.list_users'))

    data = {
        'title': 'Change User Password',
        'form': form,
        'user': user,
    }
    return render_template('admin/users/change_password.html', **data)


@admin.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm(request.form)
    if request.method == 'POST' and form.validate():
        current_user.password = form.password.data
        db.session.add(current_user)
        db.session.commit()

        flash('Password changed successfully', 'success')
        return redirect(url_for('admin.dashboard'))

    data = {
        'title': 'Change Password',
        'form': form,
    }
    return render_template('admin/change_password.html', **data)
