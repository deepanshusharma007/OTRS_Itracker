from flask import request, jsonify, make_response, Response
from models import User
from functools import wraps
import jwt


SECRET_KEY = 'mysecretkey12345'

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')

        if not token:
            return jsonify({'message': 'Missing token'}), 401

        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            # return data
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token expired'}), 401
        except jwt.DecodeError:
            return jsonify({'message': 'Invalid token'}), 401

        # kwargs['current_user'] = data
        return f(*args, **kwargs)

    return decorated