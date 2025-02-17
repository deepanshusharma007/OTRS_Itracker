from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

from sqlalchemy import Index

# app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@localhost:3306/OTRS_ticketing_db'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy()
# db.init_app(app)

class CustomerMaster(db.Model):
    __tablename__ = 'customer_master'

    customer_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    customer_name = db.Column(db.String(255), nullable=False)
    customer_address = db.Column(db.Text, nullable=True)
    customer_website = db.Column(db.String(255), nullable=True)
    customer_email = db.Column(db.String(255), nullable=True)
    customer_logo = db.Column(db.LargeBinary, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now())
    # updated_at = db.Column(db.DateTime, default=datetime.now(), onupdate=datetime.now(), nullable=True)
    updated_at = db.Column(db.DateTime, nullable=True)
    active_flag = db.Column(db.Enum('0', '1', '2'), nullable=False)
    is_encrypted = db.Column(db.Boolean, nullable=False, default=False)

    __table_args__ = (
        Index('customer_master_customer_id', 'customer_id'),
        Index('customer_master_customer_name', 'customer_name'),
        # Index('customer_master_customer_address', 'customer_address'),
        # Index('customer_master_customer_website', 'customer_website'),
        Index('customer_master_customer_email', 'customer_email'),
        # Index('customer_master_customer_logo', 'customer_logo'),
        Index('customer_master_created_at', 'created_at'),
        Index('customer_master_updated_at', 'updated_at'),
        Index('customer_master_active_flag', 'active_flag'),
        Index('customer_master_is_encrypted', 'is_encrypted'),
    )


class User(db.Model):
    __tablename__ = 'user'

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    customer_id = db.Column(db.Integer, nullable=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    email = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    password = db.Column(db.String(255), nullable=False)
    role_id = db.Column(db.Integer, nullable=False)
    active_flag = db.Column(db.Enum('0', '1', '2'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now())
    # updated_at = db.Column(db.DateTime, default=datetime.now(), onupdate=datetime.now())
    updated_at = db.Column(db.DateTime, nullable=True)
    user_photo = db.Column(db.LargeBinary, nullable=True)
    is_encrypted = db.Column(db.Boolean, nullable=False, default=False)
    first_login = db.Column(db.Boolean, nullable=True, default=True)

    __table_args__ = (
        Index('user_user_id', 'user_id'),
        Index('user_customer_id', 'customer_id'),
        Index('user_username', 'username'),
        Index('user_email', 'email'),
        Index('user_phone', 'phone'),
        Index('user_password', 'password'),
        Index('user_role_id', 'role_id'),
        Index('user_active_flag', 'active_flag'),
        Index('user_created_at', 'created_at'),
        Index('user_updated_at', 'updated_at'),
        # Index('user_user_photo', 'user_photo'),
        Index('user_is_encrypted', 'is_encrypted'),
        Index('user_first_login', 'first_login'),
    )


class LoggedInUsers(db.Model):
    __tablename__ = 'logged_in_users'

    srno = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userid = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    customer_id = db.Column(db.Integer, nullable=False)
    active_token = db.Column(db.Text, nullable=False)
    is_logout = db.Column(db.Boolean, nullable=False, default=False)
    loggedin_at = db.Column(db.DateTime, default=datetime.now())
    logout_at = db.Column(db.DateTime, nullable=True)
    is_encrypted = db.Column(db.Boolean, nullable=False, default=False)

    __table_args__ = (
        Index('logged_in_user_srno', 'srno'),
        Index('logged_in_user_userid', 'userid'),
        Index('logged_in_user_customer_id', 'customer_id'),
        # Index('logged_in_user_active_token', 'active_token'),
        Index('logged_in_user_is_logout', 'is_logout'),
        Index('logged_in_user_loggedin_at', 'loggedin_at'),
        Index('logged_in_user_logout_at', 'logout_at'),
        Index('logged_in_user_is_encrypted', 'is_encrypted'),
    )


class Otp(db.Model):
    __tablename__ = 'otp'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userid = db.Column(db.Integer, nullable=False)
    uuid = db.Column(db.String(36), nullable=False)
    token = db.Column(db.Text, nullable=False)
    otp = db.Column(db.String(100), nullable=False)
    verified_flag = db.Column(db.Enum('0', '1'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now())
    verified_at = db.Column(db.DateTime, nullable=True)
    is_encrypted = db.Column(db.Boolean, nullable=False, default=False)

    __table_args__ = (
        Index('otp_id', 'id'),
        Index('otp_userid', 'userid'),
        Index('otp_uuid', 'uuid'),
        # Index('otp_token', 'token'),
        Index('otp_otp', 'otp'),
        Index('otp_verified_flag', 'verified_flag'),
        Index('otp_created_at', 'created_at'),
        Index('otp_verified_at', 'verified_at'),
        Index('otp_is_encrypted', 'is_encrypted'),
    )


class UserGroups(db.Model):
    __tablename__ = 'user_groups'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_group = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, nullable=True)
    customer_id = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, default=datetime.now(), onupdate=datetime.now())
    is_encrypted = db.Column(db.Boolean, nullable=False, default=False)

    __table_args__ = (
        Index('user_groups_id', 'id'),
        Index('user_groups_user_group', 'user_group'),
        Index('user_groups_user_id', 'user_id'),
        Index('user_groups_customer_id', 'customer_id'),
        Index('user_groups_created_at', 'created_at'),
        Index('user_groups_updated_at', 'updated_at'),
        Index('user_groups_is_encrypted', 'is_encrypted'),
    )


class FunctionMaster(db.Model):
    __tablename__ = 'function_master'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    function_name = db.Column(db.String(255), nullable=False)
    function_code = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now())
    is_encrypted = db.Column(db.Boolean, nullable=False, default=False)

    __table_args__ = (
        Index('function_master_id', 'id'),
        Index('function_master_function_name', 'function_name'),
        Index('function_master_function_code', 'function_code'),
        Index('function_master_created_at', 'created_at'),
        Index('function_master_is_encrypted', 'is_encrypted'),
    )


class RoleMaster(db.Model):
    __tablename__ = 'role_master'

    role_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    role_name = db.Column(db.String(255), nullable=False)
    is_encrypted = db.Column(db.Boolean, nullable=False, default=False)

    __table_args__ = (
        Index('role_master_role_id', 'role_id'),
        Index('role_master_role_name', 'role_name'),
        Index('role_master_is_encrypted', 'is_encrypted'),
    )


class RoleFunctionMapping(db.Model):
    __tablename__ = 'role_function_mapping'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    role_id = db.Column(db.Integer, nullable=False)
    function_id = db.Column(db.Integer, nullable=False)
    customer_id = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now())
    is_encrypted = db.Column(db.Boolean, nullable=False, default=False)

    __table_args__ = (
        Index('role_function_mapping_id', 'id'),
        Index('role_function_mapping_role_id', 'role_id'),
        Index('role_function_mapping_function_id', 'function_id'),
        Index('role_function_mapping_customer_id', 'customer_id'),
        Index('role_function_mapping_created_at', 'created_at'),
        Index('role_function_mapping_is_encrypted', 'is_encrypted'),
    )


class TicketType(db.Model):
    __tablename__ = 'ticket_type'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ticket_code = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(255), nullable=False, index=True)  # Ensure the 'name' column has an index
    created_at = db.Column(db.DateTime, default=datetime.now())
    is_encrypted = db.Column(db.Boolean, nullable=False, default=False)

    __table_args__ = (
        Index('ticket_type_id', 'id'),
        Index('ticket_type_ticket_code', 'ticket_code'),
        Index('ticket_type_name', 'name'),
        Index('ticket_type_created_at', 'created_at'),
        Index('ticket_type_is_encrypted', 'is_encrypted'),
    )


class TicketMaster(db.Model):
    __tablename__ = 'ticket_master'

    ticket_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    customer_id = db.Column(db.Integer, nullable=False)
    type = db.Column(db.String(255), nullable=True)
    raised_at = db.Column(db.DateTime, nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    severity = db.Column(db.String(255), nullable=False)
    priority = db.Column(db.String(255), nullable=False)
    remark = db.Column(db.JSON, nullable=True)
    raised_by_id = db.Column(db.Integer, nullable=True)
    updated_at = db.Column(db.DateTime, nullable=True)
    bucket = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(255), nullable=True)
    resolved_by_id = db.Column(db.Integer, nullable=True)
    file_paths = db.Column(db.Text, nullable=True)  # Store JSON-encoded array if needed
    is_encrypted = db.Column(db.Boolean, nullable=False, default=False)
    alert_id = db.Column(db.String(255), nullable=True)
    tracking_id = db.Column(db.String(255), nullable=True)

    __table_args__ = (
        Index('ticket_master_ticket_id', 'ticket_id'),
        Index('ticket_master_customer_id', 'customer_id'),
        Index('ticket_master_type', 'type'),
        Index('ticket_master_raised_at', 'raised_at'),
        Index('ticket_master_title', 'title'),
        # Index('ticket_master_description', 'description'),
        Index('ticket_master_severity', 'severity'),
        Index('ticket_master_priority', 'priority'),
        # Index('ticket_master_remark', 'remark'),
        Index('ticket_master_raised_by_id', 'raised_by_id'),
        Index('ticket_master_updated_at', 'updated_at'),
        Index('ticket_master_bucket', 'bucket'),
        Index('ticket_master_status', 'status'),
        Index('ticket_master_resolved_by_id', 'resolved_by_id'),
        #  Index('ticket_master_file_paths', 'file_paths'),
        Index('ticket_master_is_encrypted', 'is_encrypted'),
        Index('ticket_master_alert_id', 'alert_id'),
        Index('ticket_master_tracking_id', 'tracking_id')
    )


class TicketTransaction(db.Model):
    __tablename__ = 'ticket_transaction'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ticket_id = db.Column(db.Integer, nullable=False)
    customer_id = db.Column(db.Integer, nullable=False)
    insert_date = db.Column(db.DateTime, nullable=False)
    level = db.Column(db.Integer, nullable=False)
    group_assigned_name = db.Column(db.String(255), nullable=True)
    user_assigned_id = db.Column(db.Integer, nullable=True)
    group_assign_flag = db.Column(db.Boolean, nullable=False)
    user_assign_flag = db.Column(db.Boolean, nullable=False)
    file_paths = db.Column(db.Text, nullable=True)  # Store JSON-encoded array if needed
    is_encrypted = db.Column(db.Boolean, nullable=False, default=False)

    __table_args__ = (
        Index('ticket_transaction_id', 'id'),
        Index('ticket_transaction_ticket_id', 'ticket_id'),
        Index('ticket_transaction_customer_id', 'customer_id'),
        Index('ticket_transaction_insert_date', 'insert_date'),
        Index('ticket_transaction_level', 'level'),
        Index('ticket_transaction_group_assigned_name', 'group_assigned_name'),
        Index('ticket_transaction_user_assigned_id', 'user_assigned_id'),
        Index('ticket_transaction_group_assign_flag', 'group_assign_flag'),
        Index('ticket_transaction_user_assign_flag', 'user_assign_flag'),
        # Index('ticket_transaction_file_paths', 'file_paths'),
        Index('ticket_transaction_is_encrypted', 'is_encrypted'),
    )


class TicketResolution(db.Model):
    __tablename__ = 'ticket_resolution'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ticket_id = db.Column(db.Integer, nullable=False)
    insert_date = db.Column(db.DateTime, nullable=False)
    customer_id = db.Column(db.Integer, nullable=False)
    transaction_id = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    resolution_by = db.Column(db.Integer, nullable=True)
    supporting_files = db.Column(db.Text, nullable=True)  # Store JSON-encoded array if needed
    is_encrypted = db.Column(db.Boolean, nullable=False, default=False)

    __table_args__ = (
        Index('ticket_resolution_id', 'id'),
        Index('ticket_resolution_ticket_id', 'ticket_id'),
        Index('ticket_resolution_insert_date', 'insert_date'),
        Index('ticket_resolution_customer_id', 'customer_id'),
        Index('ticket_resolution_transaction_id', 'transaction_id'),
        Index('ticket_resolution_title', 'title'),
        # Index('ticket_resolution_description', 'description'),
        Index('ticket_resolution_resolution_by', 'resolution_by'),
        # Index('ticket_resolution_supporting_files', 'supporting_files'),
        Index('ticket_resolution_is_encrypted', 'is_encrypted'),
    )


class Workflow(db.Model):
    __tablename__ = 'workflow'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    customer_id = db.Column(db.Integer, nullable=False)
    order = db.Column(db.Integer, nullable=False)
    user_group_name = db.Column(db.String(255), nullable=False)
    parent_customer_id = db.Column(db.Integer, nullable=True)
    sla_id = db.Column(db.Integer, nullable=True)
    initiator_group = db.Column(db.String(255), nullable=True)
    terminator_group = db.Column(db.String(255), nullable=True)
    can_pickup = db.Column(db.String(255), nullable=True)
    can_transfer = db.Column(db.String(255), nullable=True)
    can_close = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False)
    is_encrypted = db.Column(db.Boolean, nullable=False, default=False)

    __table_args__ = (
        Index('workflow_id', 'id'),
        Index('workflow_customer_id', 'customer_id'),
        Index('workflow_order', 'order'),
        Index('workflow_user_group_name', 'user_group_name'),
        Index('workflow_parent_customer_id', 'parent_customer_id'),
        Index('workflow_sla_id', 'sla_id'),
        Index('workflow_initiator_group', 'initiator_group'),
        Index('workflow_terminator_group', 'terminator_group'),
        Index('workflow_can_pickup', 'can_pickup'),
        Index('workflow_can_transfer', 'can_transfer'),
        Index('workflow_can_close', 'can_close'),
        Index('workflow_created_at', 'created_at'),
        Index('workflow_is_encrypted', 'is_encrypted'),
    )


class SLAMaster(db.Model):
    __tablename__ = 'SLA_master'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    customer_id = db.Column(db.Integer, nullable=False)
    sub_customer_id = db.Column(db.Integer, nullable=True)
    severity = db.Column(db.String(255), nullable=True)
    priority = db.Column(db.String(255), nullable=True)
    ticket_type = db.Column(db.String(255), nullable=True)
    response_time_sla = db.Column(db.Integer, nullable=True)
    resolve_time_sla = db.Column(db.Integer, nullable=True)
    business_hr_bypass = db.Column(db.String(255), nullable=True)
    holiday_hour_bypass = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False)
    is_encrypted = db.Column(db.Boolean, nullable=False, default=False)

    __table_args__ = (
        Index('sla_master_id', 'id'),
        Index('sla_master_customer_id', 'customer_id'),
        Index('sla_master_sub_customer_id', 'sub_customer_id'),
        Index('sla_master_severity', 'severity'),
        Index('sla_master_priority', 'priority'),
        Index('sla_master_ticket_type', 'ticket_type'),
        Index('sla_master_response_time_sla', 'response_time_sla'),
        Index('sla_master_resolve_time_sla', 'resolve_time_sla'),
        Index('sla_master_business_hr_bypass', 'business_hr_bypass'),
        Index('sla_master_holiday_hour_bypass', 'holiday_hour_bypass'),
        Index('sla_master_created_at', 'created_at'),
        Index('sla_master_is_encrypted', 'is_encrypted'),
    )


class TicketEventLog(db.Model):
    __tablename__ = 'ticket_event_log'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ticket_id = db.Column(db.Integer, nullable=False)
    event_description = db.Column(db.String(255), nullable=False)
    event_datetime = db.Column(db.DateTime, nullable=False)
    is_encrypted = db.Column(db.Boolean, nullable=False, default=False)

    __table_args__ = (
        Index('ticket_event_log_id', 'id'),
        Index('ticket_event_log_ticket_id', 'ticket_id'),
        Index('ticket_event_log_event_description', 'event_description'),
        Index('ticket_event_log_event_datetime', 'event_datetime'),
        Index('ticket_event_log_is_encrypted', 'is_encrypted'),
    )


class SLALog(db.Model):
    __tablename__ = 'SLA_log'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    customer_id = db.Column(db.Integer, nullable=False)
    sub_customer_id = db.Column(db.Integer, nullable=True)
    ticket_id = db.Column(db.Integer, nullable=False)
    sla_start = db.Column(db.DateTime, nullable=False)
    sla_due = db.Column(db.DateTime, nullable=False)
    ticket_status = db.Column(db.String(255), nullable=False)
    sla_status = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    is_encrypted = db.Column(db.Boolean, nullable=False, default=False)
    sla_type = db.Column(db.String(255), nullable=False)

    __table_args__ = (
        Index('sla_log_id', 'id'),
        Index('sla_log_customer_id', 'customer_id'),
        Index('sla_log_sub_customer_id', 'sub_customer_id'),
        Index('sla_log_ticket_id', 'ticket_id'),
        Index('sla_log_sla_start', 'sla_start'),
        Index('sla_log_sla_due', 'sla_due'),
        Index('sla_log_ticket_status', 'ticket_status'),
        Index('sla_log_sla_status', 'sla_status'),
        Index('sla_log_created_at', 'created_at'),
        Index('sla_log_is_encrypted', 'is_encrypted'),
        Index('sla_log_sla_type', 'sla_type'),
    )


class HolidayMaster(db.Model):
    __tablename__ = 'holiday_master'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    customer_id = db.Column(db.Integer, nullable=False)
    day = db.Column(db.Date, nullable=False)
    description = db.Column(db.String(255), nullable=True)
    is_encrypted = db.Column(db.Boolean, nullable=False, default=False)

    __table_args__ = (
        Index('holiday_master_id', 'id'),
        Index('holiday_master_customer_id', 'customer_id'),
        Index('holiday_master_day', 'day'),
        Index('holiday_master_description', 'description'),
        Index('holiday_master_is_encrypted', 'is_encrypted'),
    )


class BusinessHour(db.Model):
    __tablename__ = 'business_hour'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    customer_id = db.Column(db.Integer, nullable=False)
    day = db.Column(db.String(255), nullable=False)
    starting_time = db.Column(db.Time, nullable=False)
    ending_time = db.Column(db.Time, nullable=False)
    weekly_holiday = db.Column(db.Boolean, nullable=False)
    is_encrypted = db.Column(db.Boolean, nullable=False, default=False)

    __table_args__ = (
        Index('business_hour_id', 'id'),
        Index('business_hour_customer_id', 'customer_id'),
        Index('business_hour_day', 'day'),
        Index('business_hour_starting_time', 'starting_time'),
        Index('business_hour_ending_time', 'ending_time'),
        Index('business_hour_weekly_holiday', 'weekly_holiday'),
        Index('business_hour_is_encrypted', 'is_encrypted'),
    )


class TicketFalseFlag(db.Model):
    __tablename__ = 'ticket_false_flag'

    srno = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ticketid = db.Column(db.Integer, nullable=False)
    is_false = db.Column(db.Boolean, nullable=False)
    date_time = db.Column(db.DateTime, default=datetime.now())

    __table_args__ = (
        Index('ticket_false_flag_srno', 'srno'),
        Index('ticket_false_flag_ticketid', 'ticketid'),
        Index('ticket_false_flag_is_false', 'is_false'),
        Index('ticket_false_flag_date_time', 'date_time'),
    )


class PasswordExpiry(db.Model):
    __tablename__ = 'password_expiry'

    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), primary_key=True)
    token = db.Column(db.Text, nullable=False)
    expiry_date = db.Column(db.DateTime, nullable=False)

    __table_args__ = (
        Index('password_expiry_user_id', 'user_id'),
        Index('password_expiry_date', 'expiry_date')
    )

# if __name__ == '__main__':
#     app.run(debug=True)
