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

class Delete_BusinessHours(Resource):
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
            # day = data.get('day')
            # starting_time = data.get('starting_time')
            # ending_time = data.get('ending_time')
            # weekly_holiday = data.get('weekly_holiday')

            existing_day = BusinessHour.query.filter_by(id=srno).first()
            if not existing_day:
                return jsonify({'message': 'Cannot delete data as this day not exist in business hours'}), 403

            db.session.delete(existing_day)
            db.session.commit()

            return jsonify({'message': 'Day Deleted Successfully'}), 200

        except Exception as e:
            print("Exception ----> ", e)
            return jsonify({'message': 'Error deleting day', 'error': str(e)}), 500