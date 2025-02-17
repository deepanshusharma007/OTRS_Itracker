from datetime import datetime
import jwt
from flask import jsonify, request
from flask_cors import cross_origin
from flask_restful import Resource
from sqlalchemy import or_

from jwtData import token_required
from models import TicketMaster, CustomerMaster, TicketTransaction, SLALog, TicketFalseFlag, db, User, RoleMaster, SLAMaster

JWT_SECRET_KEY = 'mysecretkey12345'


class CustomerAPI(Resource):
    @cross_origin()
    @token_required
    def post(self):
        try:
            data = request.get_json()
            print('data--> ', data)

            # Customer details
            customer_name = data.get('customer_name')
            customer_address = data.get('customer_address')
            website = data.get('website')
            email = data.get('customer_email')

            # User details
            username = data.get('username')
            user_email = data.get('user_email')
            phone = data.get('phone')
            password = data.get('password')
            role = data.get('role')

            # Validate required fields
            if not all([customer_name, customer_address, website, email, username, user_email, phone, password, role]):
                return jsonify({'error': 'Please provide all required fields'}), 400

            with db.session.begin():  # Start a transaction
                # Check if customer already exists
                existing_customer = CustomerMaster.query.filter(
                    or_(CustomerMaster.customer_email == email, CustomerMaster.customer_name == customer_name)
                ).first()

                if existing_customer:
                    return jsonify({'error': 'Customer already exists'}), 400

                # Check if username already exists
                existing_user = User.query.filter_by(username=username).first()
                if existing_user:
                    return jsonify({'error': 'Username already exists'}), 400

                # Create new customer
                new_customer = CustomerMaster(
                    customer_name=customer_name,
                    customer_address=customer_address,
                    customer_website=website,
                    customer_email=email,
                    created_at=datetime.now(),
                    active_flag='1'
                )
                db.session.add(new_customer)
                db.session.flush()  # Assign customer_id without committing
                customer_id = new_customer.customer_id

                # Retrieve role_id based on role_name
                role_record = RoleMaster.query.filter_by(role_name=role).first()
                if not role_record:
                    raise ValueError("Invalid role name")  # This will trigger a rollback
                role_id = role_record.role_id

                # Create new user
                new_user = User(
                    customer_id=customer_id,
                    username=username,
                    email=user_email,
                    phone=phone,
                    password=password,
                    role_id=role_id,
                    active_flag='1',
                    created_at=datetime.now()
                )
                db.session.add(new_user)
                db.session.flush()  # Assign user_id without committing

                ## Now adding data in SLA_master for current onboarded customer
                for ticket_type in ['SR', 'IR']:
                    for severity in ['S1', 'S2', 'S3', 'S4']:
                        response_time_sla = 360
                        resolve_time_sla = 1440
                        priority = {'S1': 'P1', 'S2': 'P2', 'S3': 'P3', 'S4': 'P4'}.get(severity)

                        # SLA entry for Protean (sub_customer_id = 1)
                        sla_entries = [
                            SLAMaster(
                                customer_id=customer_id,
                                sub_customer_id=1,
                                severity=severity,
                                priority=priority,
                                ticket_type=ticket_type,
                                response_time_sla=response_time_sla,
                                resolve_time_sla=resolve_time_sla,
                                business_hr_bypass='Y',
                                holiday_hour_bypass='Y',
                                created_at=datetime.now(),
                                is_encrypted=0
                            )
                        ]

                        # SLA entry for self (sub_customer_id = customer_id) only if customer_id != 1
                        if customer_id != 1:
                            sla_entries.append(SLAMaster(
                                customer_id=customer_id,
                                sub_customer_id=customer_id,
                                severity=severity,
                                priority=priority,
                                ticket_type=ticket_type,
                                response_time_sla=response_time_sla,
                                resolve_time_sla=resolve_time_sla,
                                business_hr_bypass='Y',
                                holiday_hour_bypass='Y',
                                created_at=datetime.now(),
                                is_encrypted=0
                            ))

                        db.session.add_all(sla_entries)

                print(f"Full SLA added successfully for customer: {customer_id}")

            # If everything succeeds, commit transaction automatically
            return jsonify({
                'message': 'Customer, User, and SLA added successfully',
                'customer_id': new_customer.customer_id,
                'user_id': new_user.user_id
            }), 201

        except ValueError as e:
            db.session.rollback()
            print(f"Business logic error: {e}")
            return jsonify({'error': str(e)}), 400

        except Exception as e:
            db.session.rollback()
            print(f"Error during customer creation: {e}")
            return jsonify({'error': 'Error creating customer', 'message': str(e)}), 500
