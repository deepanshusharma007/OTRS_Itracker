import jwt
from datetime import datetime, timedelta

from flask import request
from flask_cors import cross_origin
from flask_jwt_extended import create_access_token, create_refresh_token

from jwtData import token_required
from models import LoggedInUsers, db
from flask_restful import Resource, reqparse

# Replace with your secret key and expiration times
JWT_SECRET_KEY = 'mysecretkey12345'
ACCESS_TOKEN_EXPIRY = timedelta(minutes=30)
REFRESH_TOKEN_EXPIRY = timedelta(days=2)

def generate_token(user_id, username, role, customerid, groupname, token_type='access'):
    if token_type == 'access':
        token = create_access_token(identity=user_id, expires_delta=timedelta(minutes=30),
                                    additional_claims={'username': username, 'userid': user_id,
                                                       'customerid': customerid, 'groupname': groupname})
    else:
        token = create_refresh_token(identity=user_id, expires_delta=timedelta(hours=8),
                                    additional_claims={'username': username, 'userid': user_id,
                                                       'customerid': customerid, 'groupname': groupname})
    # token = jwt.encode(payload, JWT_SECRET_KEY, algorithm='HS256')
    return token

def decode_access_token(token):
    payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'], options={"verify_signature": False})
    return payload

def decode_token(token):
    payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
    return payload


class TokenRefreshAPI(Resource):
    @cross_origin()
    # @token_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('refreshToken', type=str, required=True, help='Refresh token is required')
        parser.add_argument('userName', type=str, required=True, help='Username is required')
        args = parser.parse_args()

        refresh_token = args['refreshToken']
        username = args['userName']

        response = self.refresh_token(refresh_token, username)
        return response

    def refresh_token(self, refresh_token, username):
        # Decode refresh token and handle errors
        try:
            decoded_refresh_token = decode_token(refresh_token)
            # print("decoded_refresh_token: ", decoded_refresh_token)
            if isinstance(decoded_refresh_token, str):
                return {'error': True, 'msg': decoded_refresh_token}, 401
        except Exception as e:
            return {'error': True, 'msg': 'Invalid refresh token'}, 401

        # Check if refresh token is expired
        if datetime.fromtimestamp(decoded_refresh_token['exp']) < datetime.now():
            return {'error': True, 'msg': 'Refresh token expired'}, 401

        # Decode access token and handle errors
        access_token = request.headers.get('Authorization')
        if not access_token:
            return {'error': True, 'msg': 'Active token missing'}, 401
        # access_token = access_token.split(' ')[1]  # Remove 'Bearer' prefix
        try:
            # print("inside try to decode access token")
            decoded_access_token = decode_access_token(access_token)
            # print("decoded_access_token: ", decoded_access_token)
            if isinstance(decoded_access_token, str):
                return {'error': True, 'msg': decoded_access_token}, 401
        except Exception as e:
            return {'error': True, 'msg': 'Invalid access token'}, 401

        # Check if usernames match
        if decoded_refresh_token['username'] != decoded_access_token['username']:
            return {'error': True, 'msg': 'Usernames do not match'}, 401

        # Generate new tokens
        user_id = decoded_refresh_token['userid']
        new_access_token = generate_token(user_id, decoded_refresh_token['username'], decoded_refresh_token['role'], decoded_refresh_token['customerid'], decoded_refresh_token['groupname'])
        new_refresh_token = generate_token(user_id, decoded_refresh_token['username'], decoded_refresh_token['role'], decoded_refresh_token['customerid'], decoded_refresh_token['groupname'], token_type='refresh')

        # Update existing tokens in database (assuming LoggedInUsers model)
        logged_in_user = LoggedInUsers.query.filter_by(userid=user_id).first()
        if logged_in_user:
            logged_in_user.active_token = new_access_token
            # logged_in_user.refresh_token = new_refresh_token
            logged_in_user.loggedin_at = datetime.now()
            db.session.commit()

        return {
            'error': False,
            'proToken': new_access_token,
            'refreshToken': new_refresh_token,
            'msg': 'New Access Token and Refresh Token generated successfully.',
            'userName': decoded_refresh_token['username'],
            'role': decoded_refresh_token['role']
        }, 201