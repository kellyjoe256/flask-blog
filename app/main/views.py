from flask import (Blueprint, render_template)

main = Blueprint(__name__, 'main')


@main.route('/')
def index():
    data = {
        'title': 'My Blog',
    }
    return render_template('main/index.html', **data)
