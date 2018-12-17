from flask import (Blueprint, render_template)

main = Blueprint('main', __name__)


@main.route('/')
def index():
    data = {
        'title': 'My Blog',
    }
    return render_template('main/index.html', **data)
