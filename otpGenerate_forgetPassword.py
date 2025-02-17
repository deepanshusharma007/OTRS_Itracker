import hashlib
import os
import smtplib
import uuid
from datetime import datetime
import random
from email.mime.text import MIMEText
from threading import Thread

from flask import jsonify, request
from flask_cors import cross_origin
from flask_restful import Resource, reqparse
from sqlalchemy import exc

from models import User, Otp, db


def send_otp_async(recipient, otp, sender_email):
    """
    Sends an email with the generated OTP to the recipient asynchronously using a thread.

    Args:
        recipient (str): Email address of the recipient.
        otp (str): The generated OTP.
        sender_email (str): Email address of the sender.
        sender_password (str): Password for the sender's email account.
    """

    sender_password = os.getenv('SMTP_PASSWORD')

    def send_otp():
        """
        Sends the email using SMTP connection within the thread.
        """

        subject = "Your OTP is: " + str(otp)
        html_message = f"""
        <!DOCTYPE html>
        <html>
        <head>
        <title>----OTP----</title>
        </head>
        <body>
        <h2>Your OTP</h2>

        <p>Dear {recipient},</p>

        <ul>
            <li><strong>OTP:</strong> {otp}</li>
        </ul>

        <p>Best regards,</p>
        <p>OTRS Support Team</p>
        </body>
        </html>
        """

        msg = MIMEText(html_message, 'html')
        msg['Subject'] = subject
        msg['From'] = sender_email
        msg['To'] = recipient

        try:
            server = smtplib.SMTP(os.getenv('SMTP_SERVER'), os.getenv('SMTP_PORT'))
            server.connect(os.getenv('SMTP_SERVER'), os.getenv('SMTP_PORT'))
            server.starttls()  # Attempt to establish TLS connection for security (optional)
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, [recipient], msg.as_string())
            print(f"OTP sent successfully to {recipient}")
        except smtplib.SMTPException as e:
            print(f"Error sending OTP via SMTP: {e}")
        finally:
            if server is not None:
                server.quit()

    # Create and start the thread
    email_thread = Thread(target=send_otp)
    email_thread.start()


class ForgotPassword(Resource):
    @cross_origin()
    def post(self):
        try:
            data = request.get_json()
            email = data.get('email')

            if not email:
                return jsonify({'error': 'Please provide email address'}), 400

            user = User.query.filter_by(email=email).first()
            if not user:
                return jsonify({'error': 'User not found'}), 404

            # Generate and send OTP
            otp = generate_otp()
            hashed_otp = hashlib.md5(str(otp).encode('utf-8')).hexdigest()

            sender_email = "SOCL1@proteantech.in"
            send_otp_async(user.email, otp, sender_email)

            # Create OTP record in the database
            otp_record = Otp(userid=user.user_id, uuid=str(uuid.uuid4()), token='NULL', otp=hashed_otp,
                             created_at=datetime.now(), verified_flag='0', is_encrypted=False)
            db.session.add(otp_record)
            db.session.commit()

            return jsonify({'message': 'OTP sent to your email'}), 200

        except Exception as e:
            db.session.rollback()
            print(f"Error sending OTP: {e}")
            return jsonify({'error': 'Error sending OTP', 'message': str(e)}), 500


def generate_otp():
    fixed_digits = 6
    return random.randrange(111111, 999999, fixed_digits)