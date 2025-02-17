from datetime import datetime

import jwt
from flask import jsonify, request
from flask_cors import cross_origin
from flask_restful import Resource, reqparse
from sqlalchemy import exc

from jwtData import token_required
from models import User, db

JWT_SECRET_KEY = 'mysecretkey12345'

class ResetPassword(Resource):
    @cross_origin()
    # @token_required
    def post(self):
        try:
            # token = request.headers.get('Authorization')
            # jwtData = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
            data = request.get_json()
            username = data.get('username')
            new_password = data.get('password')

            if not username or not new_password:
                return jsonify({'error': 'Please provide username and new password'}), 400

            user = User.query.filter_by(username=username).first()
            if not user:
                return jsonify({'error': 'User not found'}), 404

            # Update the user's password
            user.password = new_password
            user.updated_at = datetime.now()
            user.first_login = False
            db.session.commit()

            return jsonify({'error': False, 'message': 'Password updated successfully'}), 200

        except exc.SQLAlchemyError as e:
            db.session.rollback()
            print(f"Error updating password: {e}")
            return jsonify({'error': 'Error updating password', 'message': str(e)}), 500