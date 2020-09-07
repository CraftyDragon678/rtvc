from flask import request, current_app, g, Response
from functools import wraps
import jwt


def auth_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        token = request.headers.get("Authorization")
        if token is None:
            return Response(status=401)

        try:
            payload = jwt.decode(token, current_app.config['JWT_SECRET_KEY'], "HS256")
        except jwt.InvalidTokenError:
            payload = None
        
        if payload is None:
            return Response(status=401)
        
        g.user = payload
        return func(*args, **kwargs)
    return wrapper
