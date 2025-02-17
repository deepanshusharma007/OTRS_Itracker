import jwt
from flask import jsonify, request
from flask_cors import cross_origin
from flask_restful import Resource
from sqlalchemy import func, distinct
from datetime import datetime, timedelta
from jwtData import token_required
from models import LoggedInUsers, db, User


JWT_SECRET_KEY = 'mysecretkey12345'


# class CountLoggedInUsers(Resource):
#     @cross_origin()
#     @token_required
#     def get(self):
#         try:
#             token = request.headers.get('Authorization')
#             jwtData = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
#             # logged_in_users_count = db.session.query(func.count(distinct(LoggedInUsers.userid))).filter_by(is_logout=False, customer_id=jwtData['customerid']).scalar()
#             logged_in_users_count = db.session.query(func.count(distinct(LoggedInUsers.userid))).filter_by(
#                 is_logout=False, customer_id=jwtData['customerid']).filter(
#                 LoggedInUsers.loggedin_at >= datetime.now() - timedelta(minutes=30)
#             ).scalar()
#             return {'logged_in_users': logged_in_users_count}
#         except Exception as e:
#             # Handle specific exceptions if needed
#             # For example:
#             # if isinstance(e, SQLAlchemyError):
#             #     # Handle database-related errors
#             #     return jsonify({'error': 'Database error'}), 500
#             return jsonify({'msg': 'Zero user active', 'error': str(e)}), 500



class CountLoggedInUsers(Resource):
    @cross_origin()
    @token_required
    def get(self):
        try:
            token = request.headers.get('Authorization')
            jwtData = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])

            # Filter users based on customer ID and active login status
            active_logins = LoggedInUsers.query.filter_by(
                is_logout=False,
                customer_id=jwtData['customerid']
            ).filter(LoggedInUsers.loggedin_at >= datetime.now() - timedelta(hours=8))

            # Get a distinct list of user IDs
            distinct_user_ids = active_logins.with_entities(LoggedInUsers.userid).distinct().all()
            print(distinct_user_ids)

            # Count active users (length of distinct user IDs)
            logged_in_users_count = len(distinct_user_ids)

            # Build user list (consider privacy implications)
            user_list = []
            for user_id in distinct_user_ids:
                user = User.query.get(user_id[0])  # Assuming user_id is a tuple with user ID
                if user:
                    user_list.append(user.username)  # Or any other relevant user information

            return {'logged_in_users': logged_in_users_count, 'user_list': user_list}

        except Exception as e:
            # Handle specific exceptions if needed
            return jsonify({'msg': 'Error retrieving data', 'error': str(e)}), 500