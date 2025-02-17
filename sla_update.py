import datetime

import jwt
from flask_cors import cross_origin
from flask_restful import Resource
from flask import request, jsonify
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_, or_
from jwtData import token_required
from models import User, UserGroups, CustomerMaster, db, Workflow, SLAMaster
from flask_jwt_extended import jwt_required, get_jwt_identity

JWT_SECRET_KEY = "mysecretkey12345"

class Update_SLA(Resource):
    @cross_origin()
    @token_required
    def put(self):
        try:
            token = request.headers.get('Authorization')
            jwtData = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
            customer_id = jwtData['customerid']

            data = request.get_json()
            print('data--> ', data)

            id = data.get('id')
            response_time = data.get('response_time_sla')
            resolve_time = data.get('resolve_time_sla')

            sla_data = SLAMaster.query.filter_by(id=id).first()
            if not sla_data:
                return jsonify({'message': 'Cannot update data in SLA as this row does not exists'}), 403

            sla_data.resolve_time_sla = resolve_time
            sla_data.response_time_sla = response_time
            db.session.commit()

            return jsonify({'message': 'Row Updated Successfully'}), 200

        except Exception as e:
            print("Exception ----> ", e)
            return jsonify({'message': 'Error updating row', 'error': str(e)}), 500