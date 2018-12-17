from time import time
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_misaka import markdown
from slugify import slugify
from bleach import clean, linkify
from werkzeug.security import gen_salt, generate_password_hash, check_password_hash

db = SQLAlchemy()


class TimestampMixin(object):
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    updated_at = db.Column(db.DateTime, onupdate=datetime.now)


class User(db.Model, TimestampMixin):
    __tablename__ = 'user'

    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    username = db.Column(db.String(30), unique=True, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    salt = db.Column(db.String(32))
    hashed_password = db.Column(db.String(128))
    active = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)

    posts = db.relationship('Post', backref='user', lazy=True)

    def __repr__(self):
        return '<User {}>'.format(self.name)

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


post_tag = db.Table('post_tag',
                    db.Column('tag_id', db.Integer,
                              db.ForeignKey('tag.tag_id'), primary_key=True),
                    db.Column('page_id', db.Integer,
                              db.ForeignKey('post.post_id'), primary_key=True)
                    )


class Post(db.Model, TimestampMixin):
    __tablename__ = 'post'

    post_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(300), nullable=False)
    content = db.Column(db.Text, nullable=False)
    content_html = db.Column(db.Text)

    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))

    def __repr__(self):
        return '<Post {}>'.format(self.title)

    @staticmethod
    def on_changed_title(target, value, oldvalue, initiator):
        slug = slugify(value)
        timestamp = str(time())
        timestamp = timestamp.split('.')[0]  # get timestamp without microseconds
        target.slug = slug + '-' + timestamp

    @staticmethod
    def on_changed_content(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p', 'img', 'table']

        html = str(markdown(value))
        target.content_html = linkify(
            clean(html, tags=allowed_tags, strip=True))


db.event.listen(Post.title, 'set', Post.on_changed_title)
db.event.listen(Post.content, 'set', Post.on_changed_content)


class Tag(db.Model, TimestampMixin):
    __tablename__ = 'tag'

    tag_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True, nullable=False)
    slug = db.Column(db.String(45), nullable=False)

    def __repr__(self):
        return '<Tag {}>'.format(self.name)

    @staticmethod
    def on_changed_name(target, value, oldvalue, initiator):
        target.slug = slugify(value)


db.event.listen(Tag.name, 'set', Tag.on_changed_name)
