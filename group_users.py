# from datetime import datetime
#
# import jwt
# from flask import jsonify, request
# from flask_cors import cross_origin
# from flask_restful import Resource, reqparse
# from sqlalchemy import desc
#
# from jwtData import token_required
# from models import TicketMaster, CustomerMaster, TicketTransaction, SLALog, TicketFalseFlag, User, UserGroups, db
#
# JWT_SECRET_KEY = 'mysecretkey12345'
#
#
# class AddUsersToGroup(Resource):
#     @cross_origin()
#     @token_required
#     def post(self):
#         try:
#             token = request.headers.get('Authorization')
#             # print("My TOKEN: ", token)
#             jwtdata = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
#             user_customer_id = jwtdata['customerid']
#             data = request.get_json()
#             print("data--> ", data)
#             group_name = data.get('group_name')
#             users = data.get('users')
#
#             if not group_name or not users:
#                 return jsonify({'error': 'Please provide group name and user IDs'}), 400
#
#             # Check if group exists
#             existing_group = UserGroups.query.filter_by(user_group=group_name).first()
#             if not existing_group:
#                 return jsonify({'error': 'Group not found'}), 400
#
#             # Validate user IDs
#             for user in users:
#                 existing_user = User.query.filter_by(username=user).first()
#                 if not existing_user:
#                     return jsonify({'error': f'User with ID {existing_user.user_id} not found'}), 400
#
#                 existing_user_group = UserGroups.query.filter_by(user_group=group_name, user_id=existing_user.user_id, customer_id=user_customer_id).first()
#                 if existing_user_group:
#                     return jsonify({'error': f'User in this group already exists.'}), 400
#
#                 # Add users to group
#                 new_group_membership = UserGroups(
#                     user_group=group_name,
#                     user_id=existing_user.user_id,
#                     customer_id=user_customer_id,
#                     created_at=datetime.now(),
#                     is_encrypted=0
#                 )
#                 db.session.add(new_group_membership)
#                 db.session.commit()
#             return jsonify({'message': 'Users added to group successfully'}), 201
#
#         except Exception as e:
#             print(f"Error adding users to group: {e}")
#             db.session.rollback()
#             return jsonify({'error': 'Error adding users to group', 'message': str(e)}), 500





















from datetime import datetime

import jwt
from flask import jsonify, request
from flask_cors import cross_origin
from flask_restful import Resource, reqparse
from sqlalchemy import desc

from jwtData import token_required
from models import TicketMaster, CustomerMaster, TicketTransaction, SLALog, TicketFalseFlag, User, UserGroups, db

JWT_SECRET_KEY = 'mysecretkey12345'


class AddUsersToGroup(Resource):
    @cross_origin()
    @token_required
    def post(self):
        try:
            token = request.headers.get('Authorization')
            # print("My TOKEN: ", token)
            jwtdata = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
            user_customer_id = jwtdata['customerid']
            data = request.get_json()
            print("data--> ", data)
            group_name = data.get('group_name')
            users = data.get('users')

            if not group_name or not users:
                return jsonify({'error': 'Please provide group name and user IDs'}), 400

            # Check if group exists
            existing_group = UserGroups.query.filter_by(user_group=group_name).first()
            if not existing_group:
                existing_group = UserGroups(
                    user_group=group_name,
                    customer_id=user_customer_id,  # Assuming customer can create groups
                    created_at=datetime.now(),
                    is_encrypted=0
                )
                db.session.add(existing_group)
                db.session.commit()

            # Validate user IDs
            for user in users:
                existing_user = User.query.filter_by(username=user).first()
                if not existing_user:
                    return jsonify({'error': f'User with ID {existing_user.user_id} not found'}), 400

                existing_user_group = UserGroups.query.filter_by(user_group=group_name, user_id=existing_user.user_id, customer_id=user_customer_id).first()
                if existing_user_group:
                    return jsonify({'error': f'User "{existing_user.username}" in this group already exists, please select users which are not pre-exist.'}), 400

                # Add users to group
                new_group_membership = UserGroups(
                    user_group=group_name,
                    user_id=existing_user.user_id,
                    customer_id=user_customer_id,
                    created_at=datetime.now(),
                    is_encrypted=0
                )
                db.session.add(new_group_membership)
                db.session.commit()
            return jsonify({'message': 'Users added to group successfully'}), 201

        except Exception as e:
            print(f"Error adding users to group: {e}")
            db.session.rollback()
            return jsonify({'error': 'Error adding users to group', 'message': str(e)}), 500