from datetime import datetime

from flask import request, jsonify
from flask_cors import cross_origin
from flask_restful import Resource

import jwt
from jwtData import token_required
from models import TicketMaster, UserGroups, TicketFalseFlag, User, db, Workflow

JWT_SECRET_KEY = 'mysecretkey12345'


class MarkTicketAsFalsePositive(Resource):
    @cross_origin()
    @token_required
    def post(self, ticket_id):
        try:
            # Extract user ID from JWT
            token = request.headers.get('Authorization')
            jwtData = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
            user_id = jwtData['userid']  # Assuming you have a function to get user ID from JWT
            customer_id = jwtData['customerid']
            print(ticket_id)
            data = request.get_json()
            print(data.get('mark'))
            mark = data.get('mark')

            # Fetch user information
            user = User.query.filter_by(user_id=user_id).first()
            if not user:
                return jsonify({'error': True, 'message': 'User not found'}), 404

            # Find the minimum order for customer_id=1
            all_groups = Workflow.query.filter_by(customer_id=1).all()
            min_order = min(group.order for group in all_groups)
            # Get all user groups excluding the one with the minimum order
            user_groups = [group for group in all_groups if group.order != min_order]
            user_group_except_min = []
            for groups in user_groups:
                user_group_except_min.append(groups.user_group_name)
            print("user_group_except_min ", user_group_except_min)

            # Check if user has L2 or L3 permissions
            # user_groups = UserGroups.query.filter_by(user_id=user_id, customer_id=1).all()
            # user_has_l2_or_l3 = any(group.user_group in ['L2', 'L3'] for group in user_groups)
            # print("user group is: ", user_has_l2_or_l3)
            if not user_group_except_min:
                return jsonify(
                    {'error': True, 'message': 'Your user-group not permitted to mark ticket as False Positive'}), 403

            # Check if the ticket exists
            # ticket = TicketMaster.query.filter_by(ticket_id=ticket_id).first()
            # if not ticket:
            #     return jsonify({'error': True, 'msg': 'Ticket not found'}), 404

            # Create a new record in the ticket_false_flag table
            if mark == 0:
                false_flag_record = TicketFalseFlag(
                    ticketid=ticket_id,
                    is_false=False,
                    date_time=datetime.now()
                )
                db.session.add(false_flag_record)
                db.session.commit()

                return jsonify(
                    {'error': False, 'message': 'Ticket Unmarked as false positive successfully', 'boolean': True}), 200
            else:
                false_flag_record = TicketFalseFlag(
                    ticketid=ticket_id,
                    is_false=True,
                    date_time=datetime.now()
                )
                db.session.add(false_flag_record)
                db.session.commit()

                return jsonify(
                    {'error': False, 'message': 'Ticket marked as false positive successfully', 'boolean': True}), 200



        except Exception as e:
            print(f"Error marking ticket as false positive: {e}")
            db.session.rollback()
            return jsonify({'error': True, 'msg': 'Internal server error'}), 500