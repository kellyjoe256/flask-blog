from flask import Flask
from config import config
from app.models import db, login_manager
from flask_debugtoolbar import DebugToolbarExtension


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    toolbar = DebugToolbarExtension()

    db.init_app(app)
    toolbar.init_app(app)
    login_manager.init_app(app)

    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'You must be logged in to access this page'
    login_manager.login_message_category = 'warning'

    from app.admin.views import admin as admin_blueprint
    app.register_blueprint(admin_blueprint, url_prefix='/admin')

    from app.auth.views import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from app.main.views import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
