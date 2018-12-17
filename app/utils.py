import re
from functools import wraps
from urllib.parse import urlparse, urljoin
from flask import abort, request, redirect
from flask_login import current_user


def is_safe_url(target):
    """
    Checks if specified target url is safe for redirection
    :param target: Target url to be head to
    :return:
    """
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
        ref_url.netloc == test_url.netloc


def guest_required(redirect_to='/'):
    """
    Checks if user is not authenticated in order to access the current url path
    :param redirect_to: URL path to redirect to if a not a guest
    :return:
    """
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
