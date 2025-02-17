import datetime
from flask import request, jsonify
from flask_cors import cross_origin
from flask_restful import Resource

from jwtData import token_required
from models import LoggedInUsers, db
from flask_jwt_extended import jwt_required, get_jwt_identity


class Logout(Resource):
    @cross_origin()
    # @token_required
    def post(self):
        try:
            # user_id = get_jwt_identity()
            token = request.headers.get('Authorization')  # Extract the token from the header

            # Fetch the logged-in user record
            logged_in_user = LoggedInUsers.query.filter_by(active_token=token).first()

            if not logged_in_user:
                return {'error': True, 'msg': 'User not logged in or invalid token'}, 401

            # Update the is_logout flag and logout_at timestamp
            logged_in_user.is_logout = True
            logged_in_user.logout_at = datetime.datetime.now()

            db.session.commit()

            return {'error': False, 'msg': 'User logged out successfully'}, 200


        except Exception as e:
            print(f"Error during logout: {e}")
            db.session.rollback()  # Rollback on errors
            return jsonify({'error': True, 'msg': 'Internal server error'}), 500
