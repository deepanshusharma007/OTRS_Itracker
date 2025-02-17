from datetime import datetime

import jwt
from flask import jsonify, request
from flask_cors import cross_origin
from flask_restful import Resource, reqparse
from sqlalchemy import desc

from jwtData import token_required
from models import TicketMaster, CustomerMaster, TicketTransaction, SLALog, TicketFalseFlag, User, db, RoleMaster

JWT_SECRET_KEY = 'mysecretkey12345'

class AdminAPI(Resource):
    @cross_origin()
    @token_required
    def post(self):
        try:
            token = request.headers.get('Authorization')
            jwtData = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
            data = request.get_json()
            print('data--> ', data)
            username = data.get('username')
            email = data.get('email')
            phone = data.get('phone')
            password = data.get('password')
            role = data.get('role')

            if role == 'admin':
                # customer_id = jwtData['customerid']
                customer_id = data.get('customer_id')
                if not username or not email or not phone or not password or not customer_id:
                    return jsonify({'error': 'Please provide all required fields'}), 400
                # Check if user already exists
                existing_user = User.query.filter_by(username=username).first()
                if existing_user:
                    # Activate existing user if inactive
                    if existing_user.active_flag != '1':
                        existing_user.active_flag = '1'
                        db.session.commit()
                        return jsonify({'message': 'Existing user activated successfully', 'user_id': existing_user.user_id}), 200
                    else:
                        return jsonify({'error': 'Username already exists and is active'}), 400
                # Retrieve role_id based on role_name
                role = RoleMaster.query.filter_by(role_name=role).first()
                if not role:
                    return jsonify({'error': 'Invalid role name'}), 400
                role_id = role.role_id
                # Create new user
                new_user = User(
                    customer_id=customer_id,
                    username=username,
                    email=email,
                    phone=phone,
                    password=password,
                    role_id=role_id,
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                    active_flag='1'
                )
                db.session.add(new_user)
                db.session.commit()
                return jsonify({'message': 'Admin user created successfully', 'user_id': new_user.user_id}), 201
            else:
                user_customer_id = jwtData['customerid']
                if not username or not email or not phone or not password or not user_customer_id:
                    return jsonify({'error': 'Please provide all required fields'}), 400
                # Check if user already exists
                existing_user = User.query.filter_by(username=username).first()
                if existing_user:
                    # Activate existing user if inactive
                    if existing_user.active_flag != '1':
                        existing_user.active_flag = '1'
                        db.session.commit()
                        return jsonify({'message': 'Existing user activated successfully', 'user_id': existing_user.user_id}), 200
                    else:
                        return jsonify({'error': 'Username already exists and is active'}), 400
                # Retrieve role_id based on role_name
                role = RoleMaster.query.filter_by(role_name=role).first()
                if not role:
                    return jsonify({'error': 'Invalid role name'}), 400
                role_id = role.role_id
                # Create new user
                new_user = User(
                    customer_id=user_customer_id,
                    username=username,
                    email=email,
                    phone=phone,
                    password=password,
                    role_id=role_id,
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                    active_flag='1'
                )
                db.session.add(new_user)
                db.session.commit()
                return jsonify({'message': 'User created successfully', 'user_id': new_user.user_id}), 201

        except Exception as e:
            print(f"Error during admin user creation: {e}")
            db.session.rollback()
            return jsonify({'error': 'Error creating admin user', 'message': str(e)}), 500