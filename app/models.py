from calendar import month_name
from datetime import datetime
from sqlalchemy import cast, func, extract, Boolean
from flask_sqlalchemy import SQLAlchemy
from markdown import markdown
from flask_login import LoginManager, UserMixin
from slugify import slugify
from bleach import clean, linkify
from werkzeug.security import (
    gen_salt, generate_password_hash, check_password_hash)
from app.utils import append_timestamp

db = SQLAlchemy()
login_manager = LoginManager()


class TimestampMixin(object):
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    updated_at = db.Column(
        db.DateTime, onupdate=datetime.now, default=datetime.now)


class User(db.Model, TimestampMixin, UserMixin):
    __tablename__ = 'user'

    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    username = db.Column(db.String(30), unique=True, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    salt = db.Column(db.String(32))
    hashed_password = db.Column(db.String(128))
    active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)

    posts = db.relationship('Post', backref='user', lazy='dynamic')

    def __repr__(self):
        return '<User: {}>'.format(self.name)

    def get_id(self):
        return self.user_id

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        salt = gen_salt(32)
        self.salt = salt
        self.hashed_password = generate_password_hash(password + salt)

    def verify_password(self, password):
        return check_password_hash(self.hashed_password, password + self.salt)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


post_tag = db.Table('post_tag',
                    db.Column('tag_id', db.Integer,
                              db.ForeignKey('tag.tag_id'),                primary_key=True),
                    db.Column('post_id', db.Integer,
                              db.ForeignKey('post.post_id'),              primary_key=True))


class Post(db.Model, TimestampMixin):
    __tablename__ = 'post'

    post_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(300), nullable=False)
    cover_image = db.Column(db.String(120))
    content = db.Column(db.Text, nullable=False)
    content_html = db.Column(db.Text)
    published = db.Column(db.Boolean)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))

    tags = db.relationship('Tag', secondary=post_tag,
                           backref=db.backref('tags', lazy='dynamic'))

    def __repr__(self):
        return '<Post: {}>'.format(self.title)

    @property
    def post_title(self):
        return self.title

    @post_title.setter
    def post_title(self, title):
        slug = slugify(title)
        slug = append_timestamp(slug)
        self.slug = slug
        self.title = title

    @staticmethod
    def on_changed_content(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'span', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'img',
                        'table']
        allowed_attributes = ['align', 'alt', 'style', 'class', 'id',
                              'src', 'href', 'title', 'target', 'lang']
        html = markdown(value, extensions=['fenced_code'])
        target.content_html = linkify(
            clean(html, tags=allowed_tags, attributes=allowed_attributes, strip=True))

    @classmethod
    def get_recent_posts(cls, total=5):
        most_recent_posts = cls.query.with_entities(cls.title, cls.slug). \
            filter(cast(Post.published, Boolean) == bool(1)). \
            order_by(cls.created_at.desc()). \
            limit(total). \
            all()
        return most_recent_posts

    @classmethod
    def get_archives(cls, total=10):
        entities = (extract('month', cls.created_at),
                    extract('year', cls.created_at),
                    func.count(cls.post_id).label('number_of_posts'))
        archives = cls.query.with_entities(*entities). \
            group_by(extract('month', cls.created_at),
                     extract('year', cls.created_at)). \
            having(func.count(cls.post_id) >= 1). \
            filter(cast(Post.published, Boolean) == bool(1)). \
            order_by(func.min(cls.created_at).desc()). \
            limit(total). \
            all()
        formatted_archives = []
        for archive in archives:
            formatted_archives.append({
                'month': month_name[int(archive[0])],
                'year': int(archive[1]),
            })
        return formatted_archives


db.event.listen(Post.content, 'set', Post.on_changed_content)


class Tag(db.Model, TimestampMixin):
    __tablename__ = 'tag'

    tag_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True, nullable=False)
    slug = db.Column(db.String(45), nullable=False)

    posts = db.relationship('Post', secondary=post_tag,
                            backref=db.backref('posts', lazy='dynamic'))

    def __repr__(self):
        return '<Tag: {}>'.format(self.name)

    @staticmethod
    def on_changed_name(target, value, oldvalue, initiator):
        target.slug = slugify(value)


db.event.listen(Tag.name, 'set', Tag.on_changed_name)
