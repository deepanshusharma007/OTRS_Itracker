import hashlib
from datetime import datetime, timedelta

from flask import request, jsonify
from flask_cors import cross_origin
from flask_restful import Resource

from models import User, Otp, db


class ValidateOTP(Resource):
    @cross_origin()
    def post(self):
        try:
            data = request.get_json()
            email = data.get('email')
            otp = data.get('otp')

            if not email or not otp:
                return jsonify({'error': 'Please provide email, OTP, and new password'}), 400

            user = User.query.filter_by(email=email).first()
            if not user:
                return jsonify({'error': 'User not found'}), 404

            hashed_otp = hashlib.md5(str(otp).encode('utf-8')).hexdigest()
            otp_record = Otp.query.filter_by(userid=user.user_id, otp=hashed_otp, verified_flag='0').first()
            if not otp_record:
                return jsonify({'error': 'Invalid OTP'}), 400

            # Check if OTP is expired
            ten_minutes_ago = datetime.now() - timedelta(minutes=10)
            if otp_record.created_at < ten_minutes_ago:
                return jsonify({'error': 'OTP expired'}), 400

            otp_record.verified_flag = '1'  # Mark OTP as verified
            db.session.commit()

            return jsonify({'message': 'OTP validated successfully'}), 200

        except Exception as e:
            db.session.rollback()
            print(f"Error validating OTP: {e}")
            return jsonify({'error': 'Error validating OTP', 'message': str(e)}), 500