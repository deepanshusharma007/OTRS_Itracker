import datetime

import jwt
from flask_cors import cross_origin
from flask_restful import Resource
from flask import request, jsonify
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_
from jwtData import token_required
from models import User, UserGroups, CustomerMaster, db, Workflow
from flask_jwt_extended import jwt_required, get_jwt_identity

JWT_SECRET_KEY = "mysecretkey12345"

class Update_Workflow(Resource):
    @cross_origin()
    @token_required
    def put(self):
        try:
            token = request.headers.get('Authorization')
            jwtData = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
            customer_id = jwtData['customerid']

            data = request.get_json()
            print('data--> ', data)

            srno = data.get('srno')
            order = data.get('order')
            user_group_name = data.get('group')
            parent_customer = data.get('main_customer')
            initiator_group = data.get('can_initiate')
            can_pickup = data.get('can_pick')
            can_transfer = data.get('can_transfer')
            can_close = data.get('can_close')

            if parent_customer=='Infosec':
                parent_customer_id=1
                existing_order = Workflow.query.filter_by(id=srno).first()
                if not existing_order:
                    return jsonify({'message': 'Cannot update data in workflow as this order does not exists'}), 403

                existing_order.order = order
                existing_order.user_group_name = user_group_name
                existing_order.parent_customer_id = parent_customer_id
                existing_order.initiator_group = initiator_group
                existing_order.can_pickup = can_pickup
                existing_order.can_transfer = can_transfer
                existing_order.can_close = can_close
                db.session.commit()

                return jsonify({'message': 'Row Updated Successfully'}), 200
            else:
                parent_customer_id = customer_id
                existing_order = Workflow.query.filter_by(id=srno).first()
                if not existing_order:
                    return jsonify({'message': 'Cannot update data in workflow as this order does not exists'}), 403

                existing_order.order = order
                existing_order.user_group_name = user_group_name
                existing_order.parent_customer_id = parent_customer_id
                existing_order.initiator_group = initiator_group
                existing_order.can_pickup = can_pickup
                existing_order.can_transfer = can_transfer
                existing_order.can_close = can_close
                db.session.commit()

                return jsonify({'message': 'Row Updated Successfully'}), 200

        except Exception as e:
            print("Exception ----> ", e)
            return jsonify({'message': 'Error updating row', 'error': str(e)}), 500