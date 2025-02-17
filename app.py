import hashlib
import os
from datetime import datetime, timedelta
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash


import logging
from logging.handlers import TimedRotatingFileHandler


from close_ticket import CloseTicket
from create_ticket import CreateTicket
from download_document import DownloadDoc
from false_positive_ticket import MarkTicketAsFalsePositive
from file_upload import FileUpload
from filters import TicketFilters
from models import db, PasswordExpiry, User
from login import Login
from flask_cors import CORS, cross_origin

from otp_validation import OtpValidation
from pickup_ticket import TicketPickup
from refreshToken import TokenRefreshAPI
from logout import Logout
from logged_in_users import CountLoggedInUsers
from Dashboard import Dashboard
from submit_resolution import SubmitResolution
from ticket_details import TicketDetails
from updateDescription import UpdateTicketDescription
from userGroupInfo import UserGroupList
from assign_ticket import AssignTicket
from customer_details import CustomerDetails
from export_ticket import ExportTicket
# from ticket_counts import TicketCounts
from onboard_customer import CustomerAPI
from admin_user import AdminAPI
from delete_user import DeleteUser
from group_users import AddUsersToGroup
from workflow_data import Data_Workflow
from workflow_insert import Insert_Workflow
from workflow_update import Update_Workflow
from workflow_delete import Delete_Workflow
from group_data import GetGroupsAndUsers
from business_hours_data import Data_BusinessHours
from business_hours_delete import Delete_BusinessHours
from business_hours_insert import Insert_BusinessHours
from business_hours_update import Update_BusinessHours
from holiday_master_insert import Insert_HolidayMaster
from holiday_master_update import Update_HolidayMaster
from holiday_master_delete import Delete_HolidayMaster
from holiday_master_data import Data_HolidayMaster
from delete_group_user import DeleteUserFromGroup
from otpGenerate_forgetPassword import ForgotPassword
from otpValidate_forgetPassword import ValidateOTP
from update_password import UpdatePassword
from reset_password import ResetPassword
from ticket_details_editable import UpdateTicketDetails
from export_multiple_tickets_zip import ExportMultipleTickets
from create_ticket_automatic import CreateTicketAutomatic
from sla_data import Data_SLA
from sla_update import Update_SLA

from waitress import serve


import redis
from flask import Flask, render_template_string, request, session, redirect, url_for, make_response, render_template, jsonify
from flask_session import Session
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv

app = Flask(__name__)
jwt = JWTManager(app)
mail = Mail(app)

load_dotenv()

cors = CORS(app, resources={r"/*": {"origins": "*"}})
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@localhost:3306/OTRS_ticketing_db'
app.config['JWT_SECRET_KEY'] = 'mysecretkey12345'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=30)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=2)
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['CORS_METHODS'] = '[”GET”, “HEAD”, “POST”, “OPTIONS”, “PUT”, “PATCH”, “DELETE”]'

app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_REDIS'] = redis.from_url(os.getenv('REDIS_URL'))
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=8)
app.config['SECRET_KEY'] = 'mysecretkey12345'

 
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER')
os.makedirs(os.getenv('UPLOAD_FOLDER'), exist_ok=True)

server_session = Session(app)

db.init_app(app)
api = Api(app)

migrate = Migrate(app, db)

api.add_resource(Login, '/api/login', methods=['POST'])
api.add_resource(OtpValidation, '/api/validate_otp', methods=['POST'])
api.add_resource(TokenRefreshAPI, '/api/refresh_token', methods=['POST'])
api.add_resource(Logout, '/api/logout', methods=['POST'])
api.add_resource(CountLoggedInUsers, '/api/logged_in_users', methods=['GET'])
api.add_resource(Dashboard, '/api/dashboard', methods=['POST'])
api.add_resource(TicketDetails, '/api/ticket_details/<int:ticket_id>', methods=['POST'])
api.add_resource(UserGroupList, '/api/user_group_list', methods=['GET'])
api.add_resource(TicketPickup, '/api/ticket_pickup/<int:ticket_id>', methods=['POST'])
api.add_resource(AssignTicket, '/api/assign_ticket/<int:ticket_id>', methods=['POST'])
api.add_resource(TicketFilters, '/api/filters', methods=['POST'])
api.add_resource(FileUpload, '/api/file_upload', methods=['POST'])
api.add_resource(DownloadDoc, '/api/download_document/<string:document_name>/<int:ticket_id>', methods=['POST'])
api.add_resource(SubmitResolution, '/api/submit_resolution/<int:ticket_id>', methods=['POST'])
api.add_resource(CloseTicket, '/api/close_ticket/<int:ticket_id>', methods=['POST'])
# api.add_resource(CreateTicket, '/api/create_ticket', methods=['POST'])
api.add_resource(CreateTicket, '/api/create_ticket_manually', methods=['POST'])
api.add_resource(CustomerDetails, '/api/customer_details', methods=['GET'])
api.add_resource(UpdateTicketDescription, '/api/update_ticket_description/<int:ticket_id>', methods=['PUT'])
api.add_resource(MarkTicketAsFalsePositive, '/api/false_positive_ticket/<int:ticket_id>', methods=['POST'])
api.add_resource(ExportTicket, '/api/export_ticket/<int:ticket_id>', methods=['GET'])
# api.add_resource(TicketCounts, '/api/ticket_counts', methods=['GET'])
api.add_resource(CustomerAPI, '/api/onboard_customer', methods=['POST'])
api.add_resource(AdminAPI, '/api/admin_user', methods=['POST'])
api.add_resource(DeleteUser, '/api/delete', methods=['POST'])
api.add_resource(AddUsersToGroup,  '/api/group_users', methods=['POST'])
api.add_resource(Data_Workflow, '/api/workflow_data', methods=['GET'])
api.add_resource(Insert_Workflow, '/api/workflow_insert', methods=['POST'])
api.add_resource(Update_Workflow, '/api/workflow_update', methods=['PUT'])
api.add_resource(Delete_Workflow, '/api/workflow_delete', methods=['POST'])
api.add_resource(GetGroupsAndUsers, '/api/get_group_users', methods=['GET'])
api.add_resource(Data_BusinessHours, '/api/business_hours_data', methods=['GET'])
api.add_resource(Insert_BusinessHours, '/api/business_hours_insert', methods=['POST'])
api.add_resource(Update_BusinessHours, '/api/business_hours_update', methods=['PUT'])
api.add_resource(Delete_BusinessHours, '/api/business_hours_delete', methods=['POST'])
api.add_resource(Data_HolidayMaster, '/api/holiday_master_data', methods=['GET'])
api.add_resource(Insert_HolidayMaster, '/api/holiday_master_insert', methods=['POST'])
api.add_resource(Update_HolidayMaster, '/api/holiday_master_update', methods=['PUT'])
api.add_resource(Delete_HolidayMaster, '/api/holiday_master_delete', methods=['POST'])
api.add_resource(DeleteUserFromGroup, '/api/delete_user_from_group', methods=['POST'])
api.add_resource(ForgotPassword, '/api/forget_password', methods=['POST'])
api.add_resource(ValidateOTP, '/api/forget_otp_validate', methods=['POST'])
api.add_resource(UpdatePassword, '/api/update_password', methods=['POST'])
api.add_resource(ResetPassword, '/api/reset_password', methods=['POST'])
api.add_resource(UpdateTicketDetails, '/api/update_ticket_details/<int:ticket_id>', methods=['PUT'])
api.add_resource(ExportMultipleTickets, '/api/export_multiple_tickets', methods=['POST'])
api.add_resource(CreateTicketAutomatic, '/api/create_ticket', methods=['POST'])
api.add_resource(Data_SLA, '/api/sla_data', methods=['GET'])
api.add_resource(Update_SLA, '/api/sla_update', methods=['PUT'])


@app.route('/api/reset_password/<token>', methods=['GET'])
def reset_password(token):
    print(token)
    token_record = PasswordExpiry.query.filter_by(token=token).first()
    if token_record and token_record.expiry_date > datetime.now():
        # Token is valid, render the password reset form
        return render_template('reset_password.html', token=token)
    else:
        # Token is invalid or expired
        return "Invalid or expired token"

@app.route('/api/reset_password/<token>', methods=['POST'])
def process_reset_password(token):
    print(token)
    token = request.form.get('token')
    old_password = request.form.get('old_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')

    print(token)
    print(new_password)
    print(confirm_password)

    token_record = PasswordExpiry.query.filter_by(token=token).first()
    if not token_record or token_record.expiry_date < datetime.now():
        return "Invalid or expired token"

    # Validate new passwords
    if new_password != confirm_password:
        return "Passwords do not match"

    # Update user's password and delete token record
    user = User.query.get(token_record.user_id)

    if hashlib.md5(str(old_password).encode('utf-8')).hexdigest() != user.password:
        return "Old password is wrong, please enter correct old password"

    if user:
        user.password = hashlib.md5(str(new_password).encode('utf-8')).hexdigest()
        user.updated_at = datetime.now()
        db.session.delete(token_record)
        db.session.commit()
        return "Password reset successful"
    else:
        return "Invalid token or user not found"

#@app.route('/api/create_ticket', methods=['POST'])
#def receive_json():
#    try:
#        # Get JSON data from the request
#        data = request.get_json()
#        if not data:
#            return jsonify({"error": "No JSON payload provided"}), 400
#
#        # Print the received JSON data to the console
#        with open('received_data.txt', 'a') as file:
#
#            file.write(str(data))#json.dump(data, file, indent=4)  # Save the JSON in a readable format
#
#        print("Received JSON data:", data)
#
#        # Respond with a success message
#        return jsonify({"message": "JSON received successfully", "data": data}), 200
#    except Exception as e:
#        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    #app.run(debug=True, host='127.0.0.1', port=8090)
    # app.run(debug=True)
    log_dir = '/data/otrs_logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
 
    # Set up logging
    log_file = os.path.join(log_dir, 'app.log')
    handler = TimedRotatingFileHandler(log_file, when='midnight', interval=1)
    handler.suffix = "%Y-%m-%d"
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)
 
    # Set the logger to handle debug level messages
    app.logger.setLevel(logging.DEBUG)
 
    # Log a message to indicate the server is starting
    app.logger.debug("Starting the Flask server with Waitress")
    serve(app, host='127.0.0.1', port=8090)
    
