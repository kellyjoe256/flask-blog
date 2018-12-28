from flask import Flask, render_template
from config import config
from app.models import db, login_manager
from flask_misaka import Misaka
from flask_wtf.csrf import CSRFProtect
from flask_debugtoolbar import DebugToolbarExtension
from flask_uploads import (UploadSet, configure_uploads, IMAGES,
                           patch_request_class)

csrf = CSRFProtect()
md = Misaka()
toolbar = DebugToolbarExtension()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'You must be logged in to access this page'
login_manager.login_message_category = 'warning'

uploads = UploadSet('uploads', IMAGES)

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    db.init_app(app)
    md.init_app(app)
    csrf.init_app(app)
    toolbar.init_app(app)
    login_manager.init_app(app)

    configure_uploads(app, uploads)
    # set maximum file size, default is 16MB
    patch_request_class(app, 1 * 1024 * 1024)

    from app.admin.views import admin as admin_blueprint
    app.register_blueprint(admin_blueprint, url_prefix='/admin')

    from app.auth.views import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from app.api.views import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api')

    from app.main.views import main as main_blueprint
    app.register_blueprint(main_blueprint)

    @app.errorhandler(403)
    def forbidden_route(e):
        return render_template('errors/403.html', e=e), 403

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html', e=e), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html', e=e), 500


    return app
