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


class Insert_Workflow(Resource):
    @cross_origin()
    @token_required
    def post(self):
        try:
            token = request.headers.get('Authorization')
            jwtData = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
            customer_id = jwtData['customerid']

            data = request.get_json()
            print('data--> ', data)

            order = data.get('order')
            user_group_name = data.get('group')
            parent_customer = data.get('main_customer')

            initiator_group = data.get('can_initiate')
            can_pickup = data.get('can_pick')
            can_transfer = data.get('can_transfer')
            can_close = data.get('can_close')

            if initiator_group == 'Yes':
                initiator_group = "Y"
            else:
                initiator_group = "N"

            if can_pickup == 'Yes':
                can_pickup = "Y"
            else:
                can_pickup = "N"

            if can_transfer == 'Yes':
                can_transfer = "Y"
            else:
                can_transfer = "N"

            if can_close == 'Yes':
                can_close = "Y"
            else:
                can_close = "N"

            if parent_customer == 'Infosec':
                parent_customer_id = 1
                existing_order = Workflow.query.filter_by(customer_id=customer_id, order=order).first()
                if existing_order:
                    return jsonify({'message': 'Order pre-exists'}), 403

                workflow = Workflow(
                    customer_id=customer_id,
                    order=order,
                    user_group_name=user_group_name,
                    parent_customer_id=parent_customer_id,
                    sla_id=1,
                    initiator_group=initiator_group,
                    terminator_group='N',
                    can_pickup=can_pickup,
                    can_transfer=can_transfer,
                    can_close=can_close,
                    created_at=datetime.datetime.now(),
                    is_encrypted=0
                )
                db.session.add(workflow)
                db.session.commit()

                return jsonify({'message': 'Row inserted successfully'}), 200
            else:
                parent_customer_id = customer_id
                existing_order = Workflow.query.filter_by(customer_id=customer_id, order=order).first()
                if existing_order:
                    return jsonify({'message': 'Order pre-exists'}), 403

                workflow = Workflow(
                    customer_id=customer_id,
                    order=order,
                    user_group_name=user_group_name,
                    parent_customer_id=parent_customer_id,
                    sla_id=1,
                    initiator_group=initiator_group,
                    terminator_group='N',
                    can_pickup=can_pickup,
                    can_transfer=can_transfer,
                    can_close=can_close,
                    created_at=datetime.datetime.now(),
                    is_encrypted=0
                )
                db.session.add(workflow)
                db.session.commit()

                return jsonify({'message': 'Row inserted successfully'}), 200

        except Exception as e:
            print("Exception ----> ", e)
            return jsonify({'message': 'Error inserting row', 'error': str(e)}), 500