import datetime

import jwt
from flask_cors import cross_origin
from flask_restful import Resource
from flask import request, jsonify
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_, distinct
from jwtData import token_required
from models import User, UserGroups, CustomerMaster, db, Workflow, BusinessHour, HolidayMaster
from flask_jwt_extended import jwt_required, get_jwt_identity

JWT_SECRET_KEY = "mysecretkey12345"

class Data_HolidayMaster(Resource):
    @cross_origin()
    @token_required
    def get(self):
        try:
            token = request.headers.get('Authorization')
            jwtData = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
            customer_id = jwtData['customerid']

            all_holidays = []

            records = HolidayMaster.query.filter_by(customer_id=customer_id).all()
            if not records:
                return jsonify({'message': 'Holiday list is empty'}), 404

            for record in records:
                print(f"customer id is {record.customer_id} and day is {record.day}")

                holiday_details = {
                    'srno': record.id,
                    'day': record.day.strftime("%a, %d %b %Y"),
                    'description': record.description
                }

                all_holidays.append(holiday_details)

            return jsonify({'message': 'successful', 'holidays': all_holidays})

        except Exception as e:
            print("Exception --> ", e)
            return jsonify({'msg': 'Error displaying holidays', 'error': str(e)})