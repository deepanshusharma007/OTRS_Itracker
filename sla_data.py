import datetime

import jwt
from flask_cors import cross_origin
from flask_restful import Resource
from flask import request, jsonify
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_, distinct, or_
from jwtData import token_required
from models import User, UserGroups, CustomerMaster, db, Workflow, SLAMaster
from flask_jwt_extended import jwt_required, get_jwt_identity

JWT_SECRET_KEY = "mysecretkey12345"

class Data_SLA(Resource):
    @cross_origin()
    @token_required
    def get(self):
        try:
            token = request.headers.get('Authorization')
            jwtData = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
            customer_id = jwtData['customerid']

            query = SLAMaster.query.filter_by(customer_id=customer_id)

            slas = query.all()

            if not slas:
                return jsonify({"message": "No SLA records found for the given criteria."}), 404

            # Convert query results to a list of dictionaries
            sla_list = []
            for sla in slas:
                sla_list.append({
                    "id": sla.id,
                    "customer_id": sla.customer_id,
                    "sub_customer_id": sla.sub_customer_id,
                    "severity": sla.severity,
                    "priority": sla.priority,
                    "ticket_type": sla.ticket_type,
                    "response_time_sla": sla.response_time_sla,
                    "resolve_time_sla": sla.resolve_time_sla,
                    "business_hr_bypass": sla.business_hr_bypass,
                    "holiday_hour_bypass": sla.holiday_hour_bypass,
                    "created_at": sla.created_at,
                    "is_encrypted": sla.is_encrypted
                })

            return jsonify({'message': 'successful', "sla_data": sla_list}), 200


        except Exception as e:
            print("Exception --> ", e)
            return jsonify({'msg': 'Error displaying sla', 'error': str(e)})