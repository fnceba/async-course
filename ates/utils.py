
from functools import wraps
#import requests
from ates_auth.models import User
from django.shortcuts import redirect


def require_auth(view):
    """
    Decorator for views that checks if the user is authenticated.
    """
    @wraps(view)
    def _wrapped_view(request, *args, **kwargs):
        if not (token:=request.getcookie('token')):
            return redirect(f'/auth?next={request.path}')
        return view(request, User.parse_user_token(token), *args, **kwargs)
    return _wrapped_view