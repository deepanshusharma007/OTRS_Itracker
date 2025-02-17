import datetime

import jwt
from flask_cors import cross_origin
from flask_restful import Resource
from flask import request, jsonify
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_, distinct
from jwtData import token_required
from models import User, UserGroups, CustomerMaster, db, Workflow, BusinessHour
from flask_jwt_extended import jwt_required, get_jwt_identity

JWT_SECRET_KEY = "mysecretkey12345"

class Data_BusinessHours(Resource):
    @cross_origin()
    @token_required
    def get(self):
        try:
            token = request.headers.get('Authorization')
            jwtData = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
            customer_id = jwtData['customerid']

            all_businesshours = []

            records = BusinessHour.query.filter_by(customer_id=customer_id).order_by(BusinessHour.id.desc()).first()
            if not records:
                return jsonify({'message': 'Business hour is empty'}), 404

            business_hour_details = {
                'srno': records.id,
                'day': records.day,
                'starting_time': str(records.starting_time),
                'ending_time': str(records.ending_time),
                'weekly_holiday': records.weekly_holiday
            }

            all_businesshours.append(business_hour_details)

            return jsonify({'message': 'successful', 'business_hours': all_businesshours})

        except Exception as e:
            print("Exception --> ", e)
            return jsonify({'msg': 'Error displaying business hours', 'error': str(e)})