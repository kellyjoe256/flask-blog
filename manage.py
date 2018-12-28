import os
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand
from app import create_app, db
from app.models import Post, User, Tag, post_tag

app = create_app(os.environ.get('FLASK_CONFIG') or 'default')

manager = Manager(app)
migrate = Migrate(app, db, compare_type=True)


def make_shell_context():
    return {
        'app': app, 
        'db': db,
        'Post': Post,
        'User': User,
        'Tag': Tag,
        'post_tag': post_tag,
    }


manager.add_command("db", MigrateCommand)
manager.add_command("shell", Shell(make_context=make_shell_context))


if __name__ == '__main__':
    manager.run()
    db.create_all()
