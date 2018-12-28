import os
import re
from time import time
from functools import wraps
from werkzeug.utils import secure_filename
from urllib.parse import urlparse, urljoin, quote_plus
from flask import abort, current_app, request, redirect, session
from flask_login import current_user


def append_timestamp(value, sep='-'):
    timestamp = str(time())
    timestamp = timestamp.split('.')[0]  # get timestamp without microseconds
    return value + sep + timestamp


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
        ref_url.netloc == test_url.netloc


def get_query_string():
    args = request.args
    query_string = ''
    if len(args):
        query_string = '?'
        for query, value in args.items():
            query_string += query + '=' + value
        query_string = query_string[0] + quote_plus(query_string[1:])
    return query_string


def guest_required(redirect_to='/'):
    def guest_required_decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if current_user.is_authenticated:
                return redirect(redirect_to)
            return func(*args, **kwargs)
        return wrapper
    return guest_required_decorator


def admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not current_user.is_admin:
            abort(403)
        return func(*args, **kwargs)
    return wrapper


def is_email(string_value):
    regex = r'^[\w.%+\-]+@[\w.\-]+\.[A-Za-z]{2,}$'
    return bool(re.search(regex, string_value, flags=re.IGNORECASE))


def allowed_file(filename, extensions=None):
    allowed_extensions = current_app.config.get(
        'ALLOWED_EXTENSIONS', extensions)
    file_extension = filename.rsplit('.', 1)[1].lower()
    return '.' in filename and \
        (allowed_extensions and file_extension in allowed_extensions)


def upload_file(post_field, upload_destination):
    info = {
        'error': None,
        'filename': '',
    }
    file = request.files.get(post_field)
    if file and file.filename == '':
        info['error'] = 'No file uploaded'
    is_allowed = allowed_file(file.filename)
    if not is_allowed:
        info['error'] = 'File type is not allowed'
    if file and is_allowed:
        filename = secure_filename(file.filename)
        file.save(os.path.join(upload_destination, filename))
        info['filename'] = filename
    return info
