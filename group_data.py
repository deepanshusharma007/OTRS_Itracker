from datetime import datetime

import jwt
from flask import jsonify, request
from flask_cors import cross_origin
from flask_restful import Resource, reqparse
from sqlalchemy import desc

from jwtData import token_required
from models import TicketMaster, CustomerMaster, TicketTransaction, SLALog, TicketFalseFlag, User, UserGroups, db

JWT_SECRET_KEY = 'mysecretkey12345'


class GetGroupsAndUsers(Resource):
    @cross_origin()
    @token_required
    def get(self):
        try:
            token = request.headers.get('Authorization')
            jwtData = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
            # data = request.get_json()
            customer_id = jwtData['customerid']

            if not customer_id:
                return jsonify({'error': 'customer ID not found'}), 400

            # Get distinct groups for the customer
            groups = db.session.query(UserGroups.user_group).filter_by(customer_id=customer_id).distinct().scalar_subquery()
            print("finding user groups: ")
            print(groups)
            user_groups = UserGroups.query.filter(UserGroups.user_group.in_(groups)).all()
            print("user groups are: --> ", user_groups)

            # Create a dictionary to store group names and user information
            group_data = {}
            for group in user_groups:
                group_name = group.user_group
                if group_name not in group_data:
                    group_data[group_name] = []

                # Check if the username already exists in the group
                if group.user_id:
                    username = User.query.filter_by(user_id=group.user_id).first().username
                if username not in group_data[group_name]:
                    group_data[group_name].append(username)

            return jsonify({'groups': group_data}), 200

        except Exception as e:
            print(f"Error retrieving user groups and users: {e}")
            return jsonify({'error': 'Error retrieving user groups and users', 'message': str(e)}), 500