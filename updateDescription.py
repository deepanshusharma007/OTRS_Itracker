import jwt
from flask import request, jsonify
from flask_cors import cross_origin
from flask_restful import Resource
from jwtData import token_required
from models import TicketMaster, UserGroups, db, User, Workflow

JWT_SECRET_KEY = 'mysecretkey12345'


class UpdateTicketDescription(Resource):
    @cross_origin()
    @token_required
    def put(self, ticket_id):
        try:
            # Extract user ID from JWT
            token = request.headers.get('Authorization')
            jwtData = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
            user_id = jwtData['userid']  # Assuming you have a function to get user ID from JWT
            customer_id = jwtData['customerid']

            # Fetch user information
            user = User.query.filter_by(user_id=user_id).first()
            if not user:
                return jsonify({'error': True, 'msg': 'User not found'}), 404

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
            # user_groups = UserGroups.query.filter_by(user_id=user_id, customer_id=customer_id).all()
            # user_has_l2_or_l3 = any(group.user_group in ['L2', 'L3'] for group in user_groups)
            # print("user belongs to: ", user_has_l2_or_l3)
            if not user_group_except_min:
                return jsonify({'error': True, 'msg': 'You are not permitted to update the description'}), 403

            # Get the new description from the request
            new_description = request.json.get('description')
            if not new_description:
                return jsonify({'error': True, 'msg': 'Description is required'}), 400

            # Update the ticket description
            ticket = TicketMaster.query.filter_by(ticket_id=ticket_id).first()
            if not ticket:
                return jsonify({'error': True, 'msg': 'Ticket not found'}), 404

            ticket.description = new_description
            db.session.commit()

            return jsonify({'message': 'Ticket description updated successfully'})

        except Exception as e:
            print(f"Error updating ticket description: {e}")
            db.session.rollback()
            return jsonify({'error': True, 'msg': 'Internal server error'}), 500