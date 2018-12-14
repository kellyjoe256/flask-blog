from flask import Flask
from config import config
from app.models import db


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    db.init_app(app)

    from app.admin.views import admin as admin_blueprint
    app.register_blueprint(admin_blueprint, prefix='/admin')

    from app.auth.views import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from app.main.views import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
