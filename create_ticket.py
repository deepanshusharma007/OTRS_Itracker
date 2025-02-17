## raise ticket--
from dotenv import load_dotenv
import os
import json
import smtplib
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from threading import Thread

from flask_mail import Mail, Message
import jwt
from flask import request, render_template, jsonify
from flask_cors import cross_origin
from flask_restful import Resource
from sqlalchemy import join

from jwtData import token_required
from models import Workflow, TicketMaster, db, TicketTransaction, SLAMaster, SLALog, TicketEventLog, User, UserGroups, \
    CustomerMaster, TicketFalseFlag, TicketResolution
from dotenv import load_dotenv

load_dotenv()

JWT_SECRET_KEY = 'mysecretkey12345'


def send_email_async(recipient, cc_recipients, subject, **kwargs):
    def send_email():
        # msg = Message(subject, recipients=[recipient])
        # msg.html = render_template(template, **kwargs)
        sender = "SOCL1@proteantech.in"
        # cc = "deepanshus@proteantech.in"
        # message = "test from python"
        print(cc_recipients)

        html_message = f"""
                                <!DOCTYPE html>
                                    <html>
                                    <head>
                                    <title>Incident: {kwargs.get('title')}</title>
                                    </head>
                                    <body>
                                    <p>Hi {kwargs.get('recipient_name')},</p>

                                    <p>The {kwargs.get('type')}: {kwargs.get('ticket_id')} has been created.</p>

                                    <table style="border: 1px solid black; border-collapse: collapse;">
                                      <tr>
                                        <th style="border: 1px solid black; padding: 5px;">Notification Details</th>
                                        <th style="border: 1px solid black; padding: 5px;"></th>
                                      </tr>
                                      <tr>
                                        <td style="border: 1px solid black; padding: 5px;">Ticket No</td>
                                        <td style="border: 1px solid black; padding: 5px;">{kwargs.get('ticket_id')}</td>
                                      </tr>
                                      <tr>
                                        <td style="border: 1px solid black; padding: 5px;">Status</td>
                                        <td style="border: 1px solid black; padding: 5px;">Open</td>
                                      </tr>
                                      <tr>
                                        <td style="border: 1px solid black; padding: 5px;">Notification Date Time</td>
                                        <td style="border: 1px solid black; padding: 5px;">{datetime.now()}</td>
                                      </tr>
                                      <tr>
                                        <td style="border: 1px solid black; padding: 5px;">Severity</td>
                                        <td style="border: 1px solid black; padding: 5px;">{kwargs.get('severity')}</td>
                                      </tr>
                                      <tr>
                                        <td style="border: 1px solid black; padding: 5px;">Description</td>
                                        <td style="border: 1px solid black; padding: 5px;">{kwargs.get('description')}</td>
                                      </tr>
                                      <tr>
                                        <td style="border: 1px solid black; padding: 5px;">Resolution</td>
                                        <td style="border: 1px solid black; padding: 5px;">{kwargs.get('remark')}</td>
                                      </tr>
                                    </table>

                                    <p>Thanks,</p>
                                    <p>OTRS Support Team</p>
                                    </body>
                                    </html>
                                    """

        msg = MIMEText(html_message, 'html')
        msg['Subject'] = subject
        msg['From'] = sender
        msg['To'] = recipient
        msg['Cc'] = ', '.join(cc_recipients)

        print("server: ", os.getenv('SMTP_SERVER'))
        print("port: ", int(os.getenv('SMTP_PORT')))

        # Direct SMTP configuration (ensure these settings match your email provider)
        # smtp_server = os.getenv('SMTP_SERVER')
        # smtp_port = int(os.getenv('SMTP_PORT'))
        # smtp_username = os.getenv('SMTP_USERNAME')
        # smtp_password = os.getenv('SMTP_PASSWORD')

        try:
            server = smtplib.SMTP(os.getenv('SMTP_SERVER'), os.getenv('SMTP_PORT'))
            server.connect(os.getenv('SMTP_SERVER'), os.getenv('SMTP_PORT'))
            server.starttls()  # Attempt to establish TLS connection for security (optional)
            server.login(sender, os.getenv('SMTP_PASSWORD'))
            server.sendmail(sender, [recipient] + cc_recipients, msg.as_string())
            print(f"Ticket created successfully")
        except smtplib.SMTPException as e:
            print(f"Error creating ticket")
        finally:
            if server is not None:
                server.quit()

    email_thread = Thread(target=send_email)
    email_thread.start()


class CreateTicket(Resource):
    @cross_origin()
    @token_required
    def get(self):
        return {'hello': 'hi'}

    @cross_origin()
    @token_required
    def post(self):
        print("..............")
        try:
            load_dotenv()
            token = request.headers.get('Authorization')
            jwtData = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
            data = request.get_json()
            print(data, "<-----------------")
            user_customer_id = jwtData['customerid']
            print(user_customer_id)
            user_id = jwtData['userid']

            user = User.query.filter_by(user_id=user_id).first()
            print(user.email)

            customer_name = data.get('customer_name')  # Assuming customer name is sent here
            # Find customer ID from customer name
            customer = CustomerMaster.query.filter_by(customer_name=customer_name).first()
            if not customer:
                return jsonify({'message': 'Customer not found'}), 400

            customer_id = customer.customer_id

            workflow_data = Workflow.query.filter_by(customer_id=customer_id).order_by(Workflow.order.asc()).first()
            print(workflow_data.user_group_name, workflow_data.parent_customer_id)

            user_group = UserGroups.query.filter_by(user_id=user.user_id).all()
            flag = 'N'
            for group in user_group:
                workflow_group = Workflow.query.filter_by(customer_id=customer_id,
                                                          user_group_name=group.user_group).first()
                if workflow_group:
                    if workflow_group.initiator_group == 'Y':
                        flag = 'Y'
                        break

            if flag == 'N':
                return jsonify({'msg': 'cannot create ticket, you are not allowed to create ticket'}), 400

            # ticket_data = TicketMaster.query.filter_by(customer_id=customer_id).first()

            # Restrict ticket type for non-admin users (customer ID != 1)
            if user_customer_id != 1 and data.get('ticketType') == "IR":
                return jsonify({'message': 'You are not authorized to raise IR tickets'}), 403

            type = data.get('ticketType')

            tracking_id = generate_tracking_id(type)
            if not tracking_id:
                return jsonify({'message': 'Invalid ticket type for tracking ID generation'}), 400

            ticketData = data.get('ticketData')
            print(ticketData)
            title = ticketData.get('title')
            print(title)
            description = ticketData.get('description')
            remark = data.get('remarks')
            severity = data.get('severity')
            print(severity)
            if severity == 'P1':
                severity = "S1"
            elif severity == 'P2':
                severity = "S2"
            elif severity == 'P3':
                severity = "S3"
            elif severity == 'P4':
                severity = "S4"
            raised_by_id = jwtData['userid']
            bucket = workflow_data.user_group_name  # group name by workflow or the user
            # bucket = data.get('bucket')
            status = "open"
            file_paths = data.get('filePath')
            print(file_paths)

            file_path = ""

            for i in file_paths:
                print(i)
                file_path += i + ", "

            file_path = file_path[:len(file_path) - 2]

            file_paths = "[" + file_path + "]"

            print("file_paths " + file_paths)

            if severity == "S1":
                priority = "P1"
            else:
                priority = "P2"

            print("passed file path")

            alert_id = data.get('alert_id')

            new_ticket = TicketMaster(
                customer_id=customer_id,
                type=type,
                raised_at=datetime.now(),
                title=title,
                description=description,
                remark=remark,
                severity=severity,
                priority=priority,
                raised_by_id=raised_by_id,
                updated_at=None,
                bucket=bucket,
                status=status,
                file_paths=file_paths,
                is_encrypted=False,
                alert_id=alert_id,
                tracking_id=tracking_id
            )
            db.session.add(new_ticket)
            db.session.commit()

            ## insert into ticket transaction
            new_transaction = TicketTransaction(
                ticket_id=new_ticket.ticket_id,
                customer_id=customer_id,
                insert_date=datetime.now(),
                level=1,
                group_assigned_name=workflow_data.user_group_name,
                group_assign_flag=True,
                user_assign_flag=False,
                file_paths=new_ticket.file_paths
            )
            db.session.add(new_transaction)
            db.session.commit()

            print("Ticket transaction-> ", new_transaction.id)

            new_ticket_resolution = TicketResolution(
                ticket_id=new_ticket.ticket_id,
                insert_date=datetime.now(),
                customer_id=customer_id,
                transaction_id=new_transaction.id,
                title=new_ticket.title,
                description=new_ticket.remark,
                resolution_by=user_id,
                supporting_files=new_ticket.file_paths
            )
            db.session.add(new_ticket_resolution)
            db.session.commit()

            print("Ticket resolution-> ", new_ticket_resolution.id)

            ## insert into ticket false flag
            new_false_positive = TicketFalseFlag(
                ticketid=new_ticket.ticket_id,
                is_false=False,
                date_time=datetime.now()
            )
            db.session.add(new_false_positive)
            db.session.commit()

            print("Ticket False positive-> ", new_false_positive.srno)

            print(type)

            ## calculate SLA
            records = SLAMaster.query.filter_by(customer_id=customer_id,
                                                sub_customer_id=workflow_data.parent_customer_id,
                                                ticket_type=type).first()
            print(records)
            print("SLA->", records.response_time_sla)

            sla_start = datetime.now()
            sla_due = sla_start + timedelta(minutes=int(records.response_time_sla))

            new_sla_log = SLALog(
                customer_id=customer_id,
                sub_customer_id=workflow_data.parent_customer_id,
                ticket_id=new_ticket.ticket_id,
                sla_start=sla_start,
                sla_due=sla_due,
                ticket_status='open',
                sla_status='not_breached',
                created_at=sla_start,
                sla_type="response_sla"
            )

            db.session.add(new_sla_log)
            db.session.commit()

            ## ticket event log

            new_ticke_eventlog = TicketEventLog(
                ticket_id=new_ticket.ticket_id,
                event_description=f"Ticket created with number:{new_ticket.ticket_id} and assigned to group {workflow_data.user_group_name}.",
                event_datetime=datetime.now()
            )
            db.session.add(new_ticke_eventlog)
            db.session.commit()

            # Get L1 users for the same customer
            # l1_users = db.session.query(User).select_from(
            #     join(User, UserGroups, User.user_id == UserGroups.user_id)
            # ).filter(
            #     UserGroups.user_group == 'L1',
            #     UserGroups.customer_id == customer_id
            # ).distinct(User.user_id).all()

            # l1_users = (((db.session.query(User)
            #               .join(UserGroups, User.user_id == UserGroups.user_id))
            #              .filter(UserGroups.user_group == "L1", UserGroups.customer_id == customer_id))
            #             .all())

            workflow_groups = db.session.query(Workflow.user_group_name).filter_by(
                customer_id=customer_id).distinct().all()
            workflow_groups = [group.user_group_name for group in workflow_groups]

            # Step 2: Find all users belonging to these groups
            users_in_groups = (db.session.query(User.email)
                               .join(UserGroups, User.user_id == UserGroups.user_id)
                               .filter(UserGroups.user_group.in_(workflow_groups))
                               .distinct().all())

            # Create a list of L1 user emails
            cc_recipients = [user.email for user in users_in_groups]

            for i in cc_recipients:
                print(i)

            recipient = user.email
            if severity == 'S1':
                severity = 'P1'
            elif severity == 'S2':
                severity = 'P2'
            elif severity == 'S3':
                severity = 'P3'
            elif severity == 'S4':
                severity = 'P4'
            # recipient = "deepanshu2210sharma@gmail.com"
            subject = f"FW: [External] {type} {new_ticket.ticket_id} | CREATED | {customer_name} | {new_ticket.title}"
            kwargs = {'ticket_id': new_ticket.ticket_id, 'title': new_ticket.title,
                      'description': new_ticket.description, 'recipient_name': user.username, 'type': type,
                      'severity': severity, 'remark': new_ticket.remark}
            send_email_async(recipient, cc_recipients, subject, **kwargs)

            return jsonify({"msg": "successful", "ticketId": new_ticket.ticket_id}), 201
        except Exception as e:
            print(e, "<<-----------------------")
            db.session.rollback()
            return jsonify({'message': 'Error creating ticket', 'error': str(e)}), 500


def generate_tracking_id(ticket_type):
    if ticket_type == 'IR':
        # Fetch the last ticket id for incident requests
        # last_ticket = TicketMaster.query.filter_by(type='IR').order_by(TicketMaster.ticket_id.desc()).first()
        last_ticket = db.session.query(TicketMaster.ticket_id).order_by(TicketMaster.ticket_id.desc()).first()
        ticket_prefix = 'INC'
    elif ticket_type == 'SR':
        # Fetch the last ticket id for service requests
        # last_ticket = TicketMaster.query.filter_by(type='SR').order_by(TicketMaster.ticket_id.desc()).first()
        last_ticket = db.session.query(TicketMaster.ticket_id).order_by(TicketMaster.ticket_id.desc()).first()
        ticket_prefix = 'SR'
    else:
        return None  # For other ticket types, return None

    if last_ticket:
        # Increment the last ticket id by 1
        last_ticket_id = last_ticket.ticket_id
        tracking_number = str(last_ticket_id + 1).zfill(5)  # Ensure 5 digits, padding with zeros if necessary
    else:
        tracking_number = '00001'  # For the first ticket in that category

    # Combine prefix and the tracking number
    tracking_id = f"{ticket_prefix}{tracking_number}"

    print("tracking id: ", tracking_id)

    return tracking_id