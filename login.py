import datetime
import os
import smtplib
import uuid
import random
from email.mime.text import MIMEText
from threading import Thread

from flask import request, jsonify
from flask_cors import cross_origin, CORS
from flask_restful import Resource


from models import User, Otp, db
import hashlib
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
from flask import Flask


load_dotenv()
app = Flask(__name__)
# from utils import send_otp


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


class Login(Resource):
    @cross_origin()
    @limiter.limit("5 per minute")
    def post(self):
        try:
            auth = request.authorization
            if not auth and not auth.username and not auth.password:
                return {'error': True, 'msg': 'Missing or invalid authorization'}, 401

            print("username is: ", auth.username)
            print("password is: ", auth.password)

            username = auth.username
            # password = hashlib.md5(str(auth.password).encode('utf-8')).hexdigest()
            password = auth.password

            # Validate user credentials
            user = User.query.filter_by(username=username).first()
            print(user.username)
            if not user or not (user.password == password) or (user.active_flag != '1'):
                return {'error': True, 'msg': 'Username or password invalid or user is not active'}, 401

            if user and user.first_login == True:
                return {'error': False, 'msg': 'First time login, please update the password',
                        'first_time_login': True}, 200

            unique_id = str(uuid.uuid4())

            # Check for existing OTP record for the user
            two_minutes_ago = datetime.datetime.now() - datetime.timedelta(minutes=2)
            existing_otp = Otp.query.filter(Otp.created_at >= two_minutes_ago).filter_by(userid=user.user_id,
                                                                                         verified_flag='0').first()

            # If OTP was generated within 2 minutes, show wait message
            if existing_otp:
                return {'error': True, 'msg': 'Please wait for a few minutes before requesting a new OTP.'}, 429
            else:
                otp = generate_otp()  # Replace with your OTP generation logic

            print(otp)
            hashed_otp = hashlib.md5(str(otp).encode('utf-8')).hexdigest()

            recipient = user.email
            # recipient = "deepanshu2210sharma@gmail.com"
            subject = "OTP Generated"
            # kwargs = {'recipient_name': user.username, 'otp': otp}
            sender_email = "SOCL1@proteantech.in"
            send_otp_async(recipient, str(otp), sender_email)

            otp_record = Otp(userid=user.user_id, uuid=unique_id, token='NULL', otp=hashed_otp,
                             created_at=datetime.datetime.now(), verified_flag='0', is_encrypted=False)
            db.session.add(otp_record)
            db.session.commit()

            # send_otp(email, otp, unique_id)

            return {'error': False, 'uniqueId': unique_id, 'otpRequest': True,
                    'msg': 'Email with otp sent to customer', 'first_time_login': False}, 201

        except Exception as e:
            print(f"Error during login: {e}")
            db.session.rollback()  # Rollback database changes on error
            return jsonify({'error': True, 'msg': 'Internal server error'}), 500


def generate_otp():
    fixed_digits = 6
    return random.randrange(111111, 999999, fixed_digits)
