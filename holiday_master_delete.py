import datetime

import jwt
from flask_cors import cross_origin
from flask_restful import Resource
from flask import request, jsonify
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_
from jwtData import token_required
from models import User, UserGroups, CustomerMaster, db, Workflow, BusinessHour, HolidayMaster
from flask_jwt_extended import jwt_required, get_jwt_identity

JWT_SECRET_KEY = "mysecretkey12345"

class Delete_HolidayMaster(Resource):
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
            # description = data.get('description')

            existing_day = HolidayMaster.query.filter_by(id=srno).first()
            if not existing_day:
                return jsonify({'message': 'Cannot delete holiday as this day not exist in holiday list'}), 403

            db.session.delete(existing_day)
            db.session.commit()

            return jsonify({'message': 'holiday Deleted Successfully'}), 200

        except Exception as e:
            print("Exception ----> ", e)
            return jsonify({'message': 'Error deleting holiday', 'error': str(e)}), 500