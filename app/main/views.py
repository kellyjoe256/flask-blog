from flask import Blueprint

main = Blueprint(__name__, 'main')


@main.route('/')
def index():
    return '<h1>Hello, World!</h1>'
