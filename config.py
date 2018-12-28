import os

basedir = os.path.abspath(os.path.dirname(__file__))
app_dir = os.path.join(basedir, 'app')


class Config(object):

    DEBUG = False
    PER_PAGE = 10
    SECRET_KEY = os.environ.get('SECRET_KEY') or \
        '\xc3\x0eF\x0c\xd8@\x9d\xc1`d+q\x04N\x1d\x15\x97\xd6\xfb\xa6S\x9ds\x89'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_DIR = os.path.join(app_dir, 'static', 'uploads')
    # Flask-Uploads Settings
    UPLOADED_FILES_ALLOW = ('png', 'jpg', 'jpeg', 'gif', 'svg')
    UPLOADED_FILES_DEST = 'uploads'
    UPLOADS_DEFAULT_DEST = os.path.join(app_dir, 'static')

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):

    ENV = 'development'
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'db.sqlite')


class ProductionConfig(Config):

    ENV = 'production'
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('PROD_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'db.sqlite')


config = {
    'development': DevelopmentConfig,
    # 'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
