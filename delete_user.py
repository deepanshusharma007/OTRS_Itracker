from datetime import datetime

import jwt
from flask import jsonify, request
from flask_cors import cross_origin
from flask_restful import Resource, reqparse
from sqlalchemy import desc

from jwtData import token_required
from models import TicketMaster, CustomerMaster, TicketTransaction, SLALog, TicketFalseFlag, User, db, RoleMaster

JWT_SECRET_KEY = 'mysecretkey12345'


class DeleteUser(Resource):
    @cross_origin()
    @token_required
    def post(self):
        try:
            data = request.get_json()
            username = data.get('username')

            if not username:
                return jsonify({'error': 'Please provide username'}), 400

            user = User.query.filter_by(username=username).first()
            if not user:
                return jsonify({'error': 'User not found'}), 404

            # Update active_flag to 0 (inactive)
            user.active_flag = 0
            db.session.commit()

            return jsonify({'message': 'User deleted successfully'}), 200

        except Exception as e:
            print(f"Error during user deletion: {e}")
            db.session.rollback()
            return jsonify({'error': 'Error deleting user', 'message': str(e)}), 500