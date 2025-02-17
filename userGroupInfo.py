import jwt
from flask_cors import cross_origin
from flask_restful import Resource
from flask import request, jsonify
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_
from jwtData import token_required
from models import User, UserGroups, CustomerMaster, db, Workflow
from flask_jwt_extended import jwt_required, get_jwt_identity

JWT_SECRET_KEY = "mysecretkey12345"


class UserGroupList(Resource):
    @cross_origin()
    @token_required  # Ensure the user is logged in
    def get(self):
        try:
            token = request.headers.get('Authorization')
            # print("My TOKEN: ", token)
            jwtdata = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
            group_name = jwtdata['groupname']
            logged_in_user_id = jwtdata['userid']
            # logged_in_user_id = get_jwt_identity()
            logged_in_user = User.query.filter_by(user_id=logged_in_user_id).first()

            print("group_name: ", group_name)

            if not logged_in_user:
                return {'error': True, 'msg': 'User not found'}, 404

            customer_id = logged_in_user.customer_id
            print("starting with customer: ", customer_id)
            groups = Workflow.query.filter_by(customer_id=customer_id).all()

            customer_groups = []
            for group in groups:
                customer_groups.append(group.user_group_name)
            # Fetch the customer name based on the customer ID
            customer = CustomerMaster.query.filter_by(customer_id=customer_id).first()
            if not customer:
                return {'error': True, 'msg': 'Customer not found'}, 404

            # if customer_id == 1 and group_name == 'L1':
            #     users = User.query.filter_by(customer_id=customer_id).all()
            #     user_groups = UserGroups.query.filter_by(customer_id=customer_id, user_group=group_name).all()
            #
            # else:
            #     # Fetch users and groups according to the rules

            if customer_id == 1 and group_name in customer_groups:
                print("inside customer id = 1")
                if group_name == "L1":
                    print("inside group name L1")
                    # If the logged-in user is from customer ID 1 (Infosec)
                    users = (
                                db.session.query(User)
                                .join(UserGroups, User.user_id == UserGroups.user_id)
                                .filter(
                                    User.customer_id == customer_id,
                                    User.active_flag == '1',
                                    UserGroups.user_group.in_(customer_groups)  # Filter users by workflow groups
                                )
                                .all()
                            )
                    # user_groups = UserGroups.query.all()
                    user_groups = Workflow.query.filter_by(customer_id=customer_id).all()
                else:
                    print("inside group name L1 else section")
                    # If the logged-in user is from customer ID 1 (Infosec)
                    # users = User.query.filter_by(customer_id=customer_id, active_flag='1').all()
                    users = (
                        db.session.query(User)
                        .join(UserGroups, User.user_id == UserGroups.user_id)
                        .filter(
                            User.customer_id == customer_id,
                            User.active_flag == '1',
                            UserGroups.user_group.in_(customer_groups)  # Filter users by workflow groups
                        )
                        .all()
                    )
                    # user_groups = UserGroups.query.all()
                    user_groups = Workflow.query.all()
            else:
                print("inside customer id = 2")
                # For users of other customers
                # users = User.query.filter_by(customer_id=customer_id, active_flag='1').all()
                users = (
                    db.session.query(User)
                    .join(UserGroups, User.user_id == UserGroups.user_id)
                    .filter(
                        User.customer_id == customer_id,
                        User.active_flag == '1',
                        UserGroups.user_group.in_(customer_groups)  # Filter users by workflow groups
                    )
                    .all()
                )

                # Fetch groups for both the logged-in customer and customer ID 1
                user_groups = Workflow.query.filter_by(customer_id=customer_id).distinct().all()

            print("completed all if else")
            print(user_groups)

            final_groups = []
            for i in user_groups:
                if i.user_group_name not in final_groups:
                    final_groups.append(i.user_group_name)
            print("final groups prepared")

            # Prepare the response
            response = {
                'customer_id': customer_id,
                'customer_name': customer.customer_name,
                'users': [{'user_id': user.user_id, 'username': user.username} for user in users],
                # 'groups': [{'group_id': group.id, 'group_name': group.user_group, 'customer_id': group.customer_id} for group in user_groups]
                'groups': [{'group_name': group} for group in final_groups]

            }

            return jsonify(response)

        except (jwt.DecodeError, jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            # Handle JWT related errors (assuming handled in token_required)
            return {'error': True, 'msg': 'Invalid or expired token'}, 401

        except (KeyError, AttributeError):  # Catch missing data in JWT
            return {'error': True, 'msg': 'Missing user information in token'}, 401

        except SQLAlchemyError as e:  # Generic SQLAlchemy error handling
            print(f"Database error: {e}")
            db.session.rollback()
            return {'error': True, 'msg': 'Internal server error'}, 500

        except Exception as e:  # Catch unexpected errors
            print(f"Unexpected error: {e}")
            db.session.rollback()
            return {'error': True, 'msg': 'Internal server error'}, 500