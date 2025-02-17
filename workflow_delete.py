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

class Delete_Workflow(Resource):
    @cross_origin()
    @token_required
    def post(self):
        try:
            token = request.headers.get('Authorization')
            jwtData = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
            customer_id = jwtData['customerid']

            data = request.get_json()
            print('data--> ', data)

            srno = data.get('srno')
            # order = data.get('order')
            # user_group_name = data.get('group')
            # parent_customer = data.get('main_customer')
            # initiator_group = data.get('can_initiate')
            # can_pickup = data.get('can_pick')
            # can_transfer = data.get('can_transfer')
            # can_close = data.get('can_close')

            existing_order = Workflow.query.filter_by(id=srno).first()
            if not existing_order:
                return jsonify({'message': 'Cannot delete data from workflow as this order does not exists'}), 403

            db.session.delete(existing_order)
            db.session.commit()

            return jsonify({'message': 'Row Deleted Successfully'}), 200

        except Exception as e:
            print("Exception ----> ", e)
            return jsonify({'message': 'Error deleting row', 'error': str(e)}), 500