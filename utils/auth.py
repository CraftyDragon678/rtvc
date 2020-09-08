from flask import request, current_app, g
from functools import wraps
import jwt
import utils


def auth_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        token = request.headers.get("Authorization")
        if token is None:
            return {"message": utils.ERROR_MESSAGES['no_token']}

        try:
            payload = jwt.decode(token, current_app.config['JWT_SECRET_KEY'], "HS256")
        except jwt.InvalidTokenError:
            payload = None
        
        if payload is None:
            return {"message": utils.ERROR_MESSAGES['not_valid_token']}
        
        g.user = payload
        return func(*args, **kwargs)
    return wrapper
