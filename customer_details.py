import jwt
from datetime import datetime, timedelta

from flask import request, jsonify
from flask_cors import cross_origin
from flask_restful import Resource, reqparse

from jwtData import token_required
from models import User, CustomerMaster

JWT_SECRET_KEY = 'mysecretkey12345'

class CustomerDetails(Resource):
    @cross_origin()
    @token_required
    def get(self):
        try:
            token = request.headers.get('Authorization')
            jwtdata = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
            user_id = jwtdata['userid']

            user = User.query.filter_by(user_id=user_id).first()
            if not user:
                return jsonify({'error': True, 'msg': 'User not found'}), 404

            customer_id = user.customer_id

            if customer_id == 1:
                customers = CustomerMaster.query.all()
                customer_data = [{'customer_id': customer.customer_id, 'customer_name': customer.customer_name} for
                                 customer in customers]
                return jsonify({'customers': customer_data})
            else:
                customer = CustomerMaster.query.filter_by(customer_id=customer_id).first()
                if not customer:
                    return {'error': True, 'msg': 'Customer not found'}, 404
                customer_data = [{'customer_id': customer.customer_id, 'customer_name': customer.customer_name}]
                return jsonify({'customers': customer_data})

        except Exception as e:
            return jsonify({'error': True, 'msg': 'An error occurred'}), 500