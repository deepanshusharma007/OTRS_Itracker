import datetime


import jwt
from dateutil import parser
from flask_cors import cross_origin
from flask_restful import Resource
from flask import request, jsonify
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_
from jwtData import token_required
from models import User, UserGroups, CustomerMaster, db, Workflow, BusinessHour, HolidayMaster
from flask_jwt_extended import jwt_required, get_jwt_identity

JWT_SECRET_KEY = "mysecretkey12345"


class Update_HolidayMaster(Resource):
    @cross_origin()
    @token_required
    def put(self):
        try:
            token = request.headers.get('Authorization')
            jwtData = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
            customer_id = jwtData['customerid']

            data = request.get_json()
            print('data--> ', data)

            srno = data['addHolidays']['srno']
            day = data['addHolidays']['day']
            description = data['addHolidays']['description']

            existing_day = HolidayMaster.query.filter_by(id=srno).first()
            if not existing_day:
                return jsonify({'message': 'Cannot update holiday as data not present in holiday list'}), 403

            print(parser.isoparse(day).date())

            # Parse the date received in ISO format
            day = parser.isoparse(day).date()

            # Add 1 day to the parsed date
            day_plus_one = day + datetime.timedelta(days=1)

            existing_day.day = day_plus_one
            existing_day.description = description
            db.session.commit()

            return jsonify({'message': 'Holiday Updated Successfully'}), 200

        except Exception as e:
            print("Exception ----> ", e)
            return jsonify({'message': 'Error updating holiday', 'error': str(e)}), 500