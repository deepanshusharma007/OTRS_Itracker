import datetime

import jwt
from flask_cors import cross_origin
from flask_restful import Resource
from flask import request, jsonify
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_
from jwtData import token_required
from models import User, UserGroups, CustomerMaster, db, Workflow, BusinessHour
from flask_jwt_extended import jwt_required, get_jwt_identity

JWT_SECRET_KEY = "mysecretkey12345"


def convert_time_format(time_in_out):
    # Assuming time_in is in "HH:MM" format
    return f"{time_in_out}:00"

class Insert_BusinessHours(Resource):
    @cross_origin()
    @token_required
    def post(self):
        try:
            token = request.headers.get('Authorization')
            jwtData = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
            customer_id = jwtData['customerid']

            data = request.get_json()
            print('data--> ', data)

            day = data['addHoursData']['day']
            starting_time = data['addHoursData']['starting_time']
            ending_time = data['addHoursData']['ending_time']
            weekly_holiday = data['addHoursData']['weekly_holiday']

            converted_starting_time = convert_time_format(starting_time)
            converted_ending_time = convert_time_format(ending_time)

            existing_day = BusinessHour.query.filter_by(customer_id=customer_id, day=day).first()
            if existing_day:
                return jsonify({'message': 'Day already present'}), 403

            businessHour = BusinessHour(
                customer_id=customer_id,
                day=day,
                starting_time=converted_starting_time,
                ending_time=converted_ending_time,
                weekly_holiday=weekly_holiday,
                is_encrypted=0
            )
            db.session.add(businessHour)
            db.session.commit()

            return jsonify({'message': 'Day inserted successfully'}), 200


        except Exception as e:
            print("Exception ----> ", e)
            return jsonify({'message': 'Error inserting Day', 'error': str(e)}), 500