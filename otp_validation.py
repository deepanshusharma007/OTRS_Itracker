import datetime
import hashlib
import os

from flask import request, jsonify, session
from flask_cors import cross_origin
from flask_restful import Resource
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv

# from sqlalchemy.sql.functions import user

from models import User, Otp, LoggedInUsers, db, RoleMaster, UserGroups
from flask_jwt_extended import create_access_token, create_refresh_token

from flask import Flask

app = Flask(__name__)
load_dotenv()

limiter = Limiter(
                get_remote_address,
                app=app,
                storage_uri=os.getenv('REDIS_URL'),
                storage_options={"socket_connect_timeout": 30},
                strategy="fixed-window", # or "moving-window"
                )
@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({
        "error": "Too many requests",
        "message": "You have exceeded the allowed number of requests. Please try again later."
    }), 429


class OtpValidation(Resource):
    @cross_origin()
    @limiter.limit("5 per minute")
    def post(self):
        try:
            print(request.get_json())
            unique_id = request.json.get('uniqueID')
            entered_otp = request.json.get('otp')
            userName = request.json.get('userName')

            hashed_entered_otp = hashlib.md5(str(entered_otp).encode('utf-8')).hexdigest()

            if not unique_id or not entered_otp:
                return {'error': True, 'msg': 'Missing required fields (uniqueId, enteredOtp)'}, 400

            # Fetch OTP record by unique ID
            otp_record = Otp.query.filter_by(uuid=unique_id).first()
            if not otp_record:
                return {'error': True, 'msg': 'Invalid unique ID'}, 400

            # Validate username against OTP record
            user = User.query.filter_by(username=userName).first()
            if not user or user.user_id != otp_record.userid:
                return {'error': True, 'msg': 'Invalid username'}, 401

            # Fetch OTPs created within the last 10 minutes
            ten_minutes_ago = datetime.datetime.now() - datetime.timedelta(minutes=10)
            otps = Otp.query.filter(Otp.created_at >= ten_minutes_ago).filter_by(uuid=unique_id).all()

            if not otps:
                return {'error': True, 'msg': 'Invalid unique ID or OTP expired'}, 400

            valid_otp = None
            for otp in otps:
                if otp.otp == hashed_entered_otp and int(otp.verified_flag) == 0:
                    valid_otp = otp
                    break
            # print(valid_otp)

            if not valid_otp:
                return {'error': True, 'msg': 'Invalid OTP'}, 401

            # Store proToken in logged_in_users table
            user = User.query.filter_by(username=userName).first()
            if not user:
                return {'error': True, 'msg': 'User not found'}, 401

            user_role = RoleMaster.query.filter_by(role_id=user.role_id).first()
            role = user_role.role_name if user_role else None

            # Get user groups
            user_groups = UserGroups.query.filter_by(user_id=user.user_id).all()
            user_group_name = None
            for i in user_groups:
                user_group_name = i.user_group

            # Generate tokens
            # access_token = create_access_token(identity=valid_otp.userid, expires_delta=datetime.timedelta(hours=8))
            # refresh_token = create_refresh_token(identity=valid_otp.userid, expires_delta=datetime.timedelta(hours=8))

            access_token = create_access_token(identity=valid_otp.userid, expires_delta=datetime.timedelta(hours=8),
                                               additional_claims={'username': userName, 'userid': valid_otp.userid,
                                                                  'customerid': user.customer_id, 'role': role,
                                                                  'groupname': user_group_name})
            refresh_token = create_refresh_token(identity=valid_otp.userid, expires_delta=datetime.timedelta(hours=8),
                                                 additional_claims={'username': userName, 'userid': valid_otp.userid,
                                                                    'customerid': user.customer_id, 'role': role,
                                                                    'groupname': user_group_name})

            logged_in_user = LoggedInUsers(userid=valid_otp.userid, customer_id=user.customer_id,
                                           active_token=access_token, is_logout=False,
                                           loggedin_at=datetime.datetime.now(), is_encrypted=False)
            db.session.add(logged_in_user)

            session['username'] = userName
            session['userid'] = valid_otp.userid
            session['customerid'] = user.customer_id
            session['role'] = role
            session['groupname'] = user_group_name

            # Update otp record
            valid_otp.verified_flag = '1'
            valid_otp.token = access_token  # Store proToken in otp table
            valid_otp.verified_at = datetime.datetime.now()

            db.session.commit()

            return {'error': False, 'proToken': access_token, 'refreshToken': refresh_token,
                    'msg': 'OTP verified successfully', 'username': userName, }, 201

        except Exception as e:
            print(f"Error during OTP validation: {e}")
            db.session.rollback()  # Rollback on errors
            return jsonify({'error': True, 'msg': 'Internal server error'}), 500
