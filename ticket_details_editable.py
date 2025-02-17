import jwt
from flask import request, jsonify
from flask_cors import cross_origin
from flask_restful import Resource
from jwtData import token_required
from models import TicketMaster, db

JWT_SECRET_KEY = 'mysecretkey12345'


class UpdateTicketDetails(Resource):
    @cross_origin()
    @token_required
    def put(self, ticket_id):
        try:
            # Extract user ID from JWT
            token = request.headers.get('Authorization')
            jwtData = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
            user_id = jwtData['userid']  # Assuming you have a function to get user ID from JWT
            customer_id = jwtData['customerid']
            user_group = jwtData['groupname']

            if user_group == "L1":
                return jsonify({'error': True, 'msg': 'L1 user cannot make changes'}), 403

            data = request.get_json()
            print(data['editableDetails'])
            full_data = data['editableDetails']

            type = full_data['type']
            severity = full_data['severity']
            alert_id = full_data['alert_id']

            ticket_details = TicketMaster.query.filter_by(ticket_id=ticket_id).first()
            ticket_details.type = type
            ticket_details.severity = severity
            ticket_details.alert_id = alert_id
            db.session.commit()

            return jsonify({'error': False, 'msg': 'Data updated successfully'}), 201


        except Exception as e:
            print(f"Error updating ticket details: {e}")
            db.session.rollback()
            return jsonify({'error': True, 'msg': 'Internal server error'}), 500