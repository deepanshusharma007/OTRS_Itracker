import json
from dotenv import load_dotenv
import os
import smtplib
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from threading import Thread

import jwt
from flask import request, jsonify, session
from flask_cors import cross_origin
from flask_mail import Mail
from flask_restful import Resource
from sqlalchemy import and_, join

from jwtData import token_required
from models import TicketMaster, db, UserGroups, User, SLALog, SLAMaster, TicketTransaction, TicketEventLog, Workflow
from sla_calculator import calculate_sla

JWT_SECRET_KEY = 'mysecretkey12345'


def send_group_email_async(recipient_emails, subject, message_body):
        def send_email():
                # msg = Message(subject, recipients=[recipient])
                # msg.html = render_template(template, **kwargs)
                sender = "SOCL1@proteantech.in"
                # cc = "deepanshus@proteantech.in"
                # message = "test from python"

                msg = MIMEText(message_body, 'html')
                msg['Subject'] = subject
                msg['From'] = sender
                msg['To'] = ', '.join(recipient_emails)
                # msg['Cc'] = ', '.join(recipient)

                print("server: ", os.getenv('SMTP_SERVER'))
                print("port: ", int(os.getenv('SMTP_PORT')))

                # Direct SMTP configuration (ensure these settings match your email provider)
                smtp_server = os.getenv('SMTP_SERVER')
                smtp_port = int(os.getenv('SMTP_PORT'))
                smtp_username = os.getenv('SMTP_USERNAME')
                smtp_password = os.getenv('SMTP_PASSWORD')

                try:
                    with smtplib.SMTP(smtp_server, smtp_port) as server:
                        server.starttls()
                        server.login(smtp_username, smtp_password)
                        # server.sendmail(sender, [recipient, cc], msg.as_string())
                        server.sendmail(sender, recipient_emails, msg.as_string())
                        print("Email sent successfully.")
                except Exception as e:
                    print("Failed to send email:", str(e))

        email_thread = Thread(target=send_email)
        email_thread.start()


def send_user_email_async(recipient, subject, message_body):
        def send_email():
                # msg = Message(subject, recipients=[recipient])
                # msg.html = render_template(template, **kwargs)
                sender = "SOCL1@proteantech.in"
                # cc = "deepanshus@proteantech.in"
                # message = "test from python"

                msg = MIMEText(message_body, 'html')
                msg['Subject'] = subject
                msg['From'] = sender
                msg['To'] = ', '.join(recipient)
                # msg['Cc'] = ', '.join(recipient)

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
                    server.sendmail(sender, recipient, msg.as_string())
                    print(f"Ticket assigned successfully")
                except smtplib.SMTPException as e:
                    print(f"Error assigning ticket")
                finally:
                    if server is not None:
                        server.quit()

        email_thread = Thread(target=send_email)
        email_thread.start()


class AssignTicket(Resource):
    @cross_origin()
    @token_required
    def get(self):
        return {'hello': 'hi'}

    @cross_origin()
    @token_required
    def post(self, ticket_id):
        print("..............")
        try:
            load_dotenv()

            data = request.get_json()
            print(data)
            token = request.headers.get("Authorization")
            jwtData = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
            # print(data, "<-----------------")
            user_customer_id = jwtData['customerid']
            print(user_customer_id)
            userid = jwtData['userid']
            user_group_name = jwtData['groupname']
            username = jwtData['username']
            ticketid = ticket_id

            ticket_customer_data = TicketMaster.query.filter_by(ticket_id=ticketid).first()
            ticket_customer_id = ticket_customer_data.customer_id
            print(ticket_customer_id)

            assign_type = data.get('assignType')  ## workflow user group
            assign_to_group = data.get('assignToGroup')
            assign_to_user = data.get('assignToUser')
            file_path = data.get('filePath')

            ## get the ticket details
            ## check ticket master bucket == username of current user

            user_workflow_data = Workflow.query.filter_by(customer_id=user_customer_id,
                                                          user_group_name=user_group_name).first()
            if user_workflow_data.can_transfer == 'N':
                return jsonify({'msg': 'You are not permitted to assign ticket'}), 404

            buckeet = TicketMaster.query.filter_by(ticket_id=ticket_id).first()
            print(buckeet.bucket, username)

            if not username == buckeet.bucket:
                return jsonify({"msg": "Ticket is not in your bucket.", "ticketId": ticket_id}), 201

            all_groups_list = Workflow.query.filter_by(customer_id=1).all()
            group_list_protean_infosec = []
            for groups in all_groups_list:
                group_list_protean_infosec.append(groups.user_group_name)

            print("groups lists of protean infosec: ", group_list_protean_infosec)

            # Find the minimum order for customer_id=1
            min_order = min(groups.order for groups in all_groups_list)
            # Find the user_group_name for the minimum order
            group_with_min_order = next(group.user_group_name for group in all_groups_list if group.order == min_order)
            # Print the user group name with the minimum order
            print(f"User group with the minimum order for customer_id=1: {group_with_min_order}")

            # Now, to find the second minimum order:
            # Sort the groups by order and then pick the second element
            sorted_groups = sorted(all_groups_list, key=lambda group: group.order)
            print("sorted_groups ", sorted_groups)
            # Initialize the minimum order and second minimum order variables
            min_order = sorted_groups[0].order
            second_min_order = None
            # Iterate through the sorted groups and find the second distinct minimum order
            for group in sorted_groups[1:]:  # Start from the second element
                if group.order != min_order:  # Check if the order is different from the minimum
                    second_min_order = group
                    break
            # Check if a second distinct minimum order was found
            if second_min_order:
                print(f"User group with the second minimum order for customer_id=1: {second_min_order.user_group_name}")
            else:
                print("There is no second distinct minimum order.")

            ## if assign type == workflow then get the data from workflow assign to next flow
            ## if logged in user cust id == 1 and next flow sub customer id is different then start sla of customer
            ## if assign type == user , check user customer id if it is same as 1 or customer id
            ## if logged in user cust id == 1 and next flow sub customer id is different then start sla of customer
            ## if assign type == group,
            "detect group from ticket id"
            ticket_severity = TicketMaster.query.filter_by(ticket_id=ticketid).first().severity
            if assign_type == "group":
                print('assigning to group')

                if user_group_name == group_with_min_order and assign_to_group == group_with_min_order:
                    return jsonify(
                        {"msg": "L1 users cannot assign tickets to other L1 groups.", "ticketId": ticket_id}), 403

                # Check if the ticket's severity is Low (S4) or Medium (S3) for L2 users
                if user_group_name == second_min_order.user_group_name and assign_to_group not in group_list_protean_infosec:
                    ticket_severity = TicketMaster.query.filter_by(ticket_id=ticketid).first().severity
                    print("ticket_severity: ", ticket_severity)
                    if ticket_severity not in ["S4", "S3"]:
                        return jsonify({"msg": "L2 users can only assign tickets with severity levels S3 or S4.",
                                        "ticketId": ticket_id}), 403

                record_exists = db.session.query(UserGroups).filter_by(user_group=assign_to_group).first()
                print("record exist: ", record_exists.customer_id)
                if (ticket_customer_id == 1 and (ticket_customer_id == record_exists.customer_id)) or (
                        (ticket_customer_id != 1) and (ticket_customer_id == record_exists.customer_id)) or (
                        assign_to_group in group_list_protean_infosec):
                    print("record exist: ", record_exists.user_id, record_exists.user_group)
                    # if not record_exists:
                    # record_exists = db.session.query(UserGroups).filter_by(user_group=assign_to_group,customer_id=1).first()
                    if record_exists:
                        # get user_id of that group
                        print(record_exists.user_id, record_exists.user_group)
                        get_customer_id_of_next_grp = db.session.query(User).filter_by(
                            user_id=record_exists.user_id).first()
                        print(get_customer_id_of_next_grp.customer_id)

                        if user_customer_id == 1 and get_customer_id_of_next_grp.customer_id != 1:
                            ## start customer sla
                            print("Customer SLA can start")

                            ## update previous sla as not breached in case of not breached from sla log table
                            latest_sla_log = SLALog.query.filter_by(ticket_id=ticket_id).order_by(
                                SLALog.id.desc()).first()
                            if latest_sla_log:
                                current_time = datetime.now()
                                breached_status = 'breached' if (
                                        current_time > latest_sla_log.sla_due and latest_sla_log.ticket_status == 'open') else 'not breached'
                                sla_log = SLALog.query.filter_by(id=latest_sla_log.id).first()
                                if sla_log:
                                    sla_log.sla_status = breached_status
                                    db.session.commit()

                            # get the sla due from sla master table
                            results = SLAMaster.query.filter(and_(
                                SLAMaster.customer_id == SLAMaster.sub_customer_id,
                                SLAMaster.sub_customer_id == ticket_customer_id,
                                SLAMaster.severity == ticket_severity,
                                SLAMaster.ticket_type == ticket_customer_data.type
                            )
                            ).first()

                            print("---->", results.response_time_sla)

                            sla_start = datetime.now()

                            if results.business_hr_bypass == "Y" and results.holiday_hour_bypass == "Y":
                                sla_due = sla_start + timedelta(minutes=int(results.response_time_sla))
                                print("done sla due normally")

                            else:
                                sla_due = calculate_sla(ticket_customer_id, sla_start, results.response_time_sla,
                                                        results.business_hr_bypass, results.holiday_hour_bypass)
                                print("done sla due by calculate sla method")

                            new_sla_log = SLALog(
                                customer_id=ticket_customer_id,
                                sub_customer_id=user_customer_id,
                                ticket_id=ticket_id,
                                sla_start=sla_start,
                                sla_due=sla_due,
                                ticket_status='open',
                                sla_status='not_breached',
                                created_at=sla_start,
                                sla_type="response_sla"
                            )
                            db.session.add(new_sla_log)
                            db.session.commit()

                        else:
                            print("Customer SLA cannot start")

                        ### insert data into ticket transaction
                        new_transaction = TicketTransaction(
                            ticket_id=ticket_id,
                            customer_id=ticket_customer_id,
                            insert_date=datetime.now(),
                            level=0,
                            group_assigned_name=assign_to_group,
                            group_assign_flag=True,
                            user_assign_flag=False,
                            file_paths=file_path
                        )
                        db.session.add(new_transaction)
                        db.session.commit()

                        ## add event logs
                        new_ticke_eventlog = TicketEventLog(
                            ticket_id=ticket_id,
                            event_description=f"User {username} assigned ticket to group {assign_to_group}.",
                            event_datetime=datetime.now()
                        )
                        db.session.add(new_ticke_eventlog)
                        db.session.commit()

                        ## update bucket from ticket master
                        ticket = TicketMaster.query.get(ticket_id)
                        if ticket:
                            ticket.bucket = assign_to_group
                            db.session.commit()

                        # assigned_group_users = (((db.session.query(User)
                        #                           .join(UserGroups, User.user_id == UserGroups.user_id))
                        #                          .filter(UserGroups.user_group == assign_to_group,
                        #                                  UserGroups.customer_id == ticket_customer_id))
                        #                         .all())
                        # print("assigned group users: ", assigned_group_users)

                        workflow_groups = db.session.query(Workflow.user_group_name).filter_by(
                            customer_id=ticket_customer_id).distinct().all()
                        workflow_groups = [group.user_group_name for group in workflow_groups]

                        # Step 2: Find all users belonging to these groups
                        assigned_group_users = (db.session.query(User.email)
                                           .join(UserGroups, User.user_id == UserGroups.user_id)
                                           .filter(UserGroups.user_group.in_(workflow_groups))
                                           .distinct().all())
                        recipient_emails = [user.email for user in assigned_group_users]

                        for i in recipient_emails:
                            print("Group user: ", i)

                        if recipient_emails:
                            # Email subject and body (replace with your desired content)
                            subject = f"FW: [External] {ticket_customer_data.type} {ticket_id} | ASSIGNED | {assign_to_group}"
                            message_body = f"""
                                <!DOCTYPE html>
                                    <html>
                                    <head>
                                    <title>Ticket Assigned</title>
                                    </head>
                                    <body>
                                    <p>Hi,</p>

                                    <p>Your ticket-{ticket_id} has been assigned to group, someone will pick it up soon.</p>

                                    <table style="border: 1px solid black; border-collapse: collapse;">
                                      <tr>
                                        <th style="border: 1px solid black; padding: 5px;">Notification Details</th>
                                        <th style="border: 1px solid black; padding: 5px;"></th>
                                      </tr>
                                      <tr>
                                        <td style="border: 1px solid black; padding: 5px;">Ticket No</td>
                                        <td style="border: 1px solid black; padding: 5px;">{ticket_id}</td>
                                      </tr>
                                      <tr>
                                        <td style="border: 1px solid black; padding: 5px;">Status</td>
                                        <td style="border: 1px solid black; padding: 5px;">Assigned</td>
                                      </tr>
                                      <tr>
                                        <td style="border: 1px solid black; padding: 5px;">Notification Date Time</td>
                                        <td style="border: 1px solid black; padding: 5px;">{datetime.now()}</td>
                                      </tr>
                                      <tr>
                                        <td style="border: 1px solid black; padding: 5px;">Severity</td>
                                        <td style="border: 1px solid black; padding: 5px;">{ticket.severity}</td>
                                      </tr>
                                      <tr>
                                        <td style="border: 1px solid black; padding: 5px;">Assigned Group</td>
                                        <td style="border: 1px solid black; padding: 5px;">{assign_to_group}</td>
                                      </tr>
                                      <tr>
                                        <td style="border: 1px solid black; padding: 5px;">Description</td>
                                        <td style="border: 1px solid black; padding: 5px;">Your ticket-{ticket_id} has been assigned to the group, someone will soon pick it up. Make your focus on the resolutions.</td>
                                      </tr>
                                      <tr>
                                        <td style="border: 1px solid black; padding: 5px;">Resolution</td>
                                        <td style="border: 1px solid black; padding: 5px;">{ticket.remark}</td>
                                      </tr>
                                    </table>

                                    <p>Thanks,</p>
                                    <p>OTRS Support Team</p>
                                    </body>
                                    </html>
                                    """

                            # Use the `send_email_async` function you defined in `create_ticket.py`
                            send_group_email_async(recipient_emails, subject, message_body)

                        return jsonify({"msg": "Ticket assigned to group", "ticketId": ticket_id}), 201
                    else:
                        return jsonify({"msg": "Group not exist", "ticketId": ticket_id}), 404
                else:
                    return jsonify({"msg": "You cannot assign ticket to this group", "ticketId": ticket_id}), 403

            if assign_type == "user":
                print("assign type user...")
                # "check assign to user's customer id == 1 or ticket customer id "
                user_Assigned_Details = User.query.filter_by(username=assign_to_user).first()
                if user_Assigned_Details:
                    print(user_Assigned_Details.customer_id)

                    # Check if the current user (L1) is trying to assign to another L1 user
                    user_Assigned_Details_group = db.session.query(UserGroups).filter_by(
                        user_id=user_Assigned_Details.user_id).first()
                    if user_group_name == group_with_min_order and user_Assigned_Details_group.user_group == group_with_min_order:
                        return jsonify(
                            {"msg": "L1 users cannot assign tickets to other L1 users.", "ticketId": ticket_id}), 403

                    # Check if the ticket's severity is Low (S4) or Medium (S3) for L2 users assigning to customers other than 1
                    if user_Assigned_Details_group.user_group == second_min_order.user_group_name and user_Assigned_Details.customer_id != 1:
                        ticket_severity = TicketMaster.query.filter_by(ticket_id=ticketid).first().severity
                        if ticket_severity not in ["S4", "S3"]:
                            return jsonify({"msg": "L2 users can only assign tickets with severity levels S3 or S4.",
                                            "ticketId": ticket_id}), 403

                    if user_Assigned_Details.customer_id == 1 or user_Assigned_Details.customer_id == ticket_customer_id:
                        print("passed")
                        if user_customer_id == 1 and user_Assigned_Details.customer_id != 1:
                            # customer sla can start
                            print("customer sla can start")

                            ## update previous sla as not breached in case of not breached from sla log table
                            latest_sla_log = SLALog.query.filter_by(ticket_id=ticket_id).order_by(
                                SLALog.id.desc()).first()
                            if latest_sla_log:
                                current_time = datetime.now()
                                breached_status = 'breached' if (
                                        current_time > latest_sla_log.sla_due and latest_sla_log.ticket_status == 'open') else 'not breached'
                                sla_log = SLALog.query.filter_by(id=latest_sla_log.id).first()
                                if sla_log:
                                    sla_log.sla_status = breached_status
                                    db.session.commit()

                            # get the sla due from sla master table
                            results = SLAMaster.query.filter(and_(
                                SLAMaster.customer_id == SLAMaster.sub_customer_id,
                                SLAMaster.sub_customer_id == ticket_customer_id,
                                SLAMaster.severity == ticket_severity,
                                SLAMaster.ticket_type == ticket_customer_data.type
                            )
                            ).first()

                            print("resolve time sla---->", results.response_time_sla)

                            sla_start = datetime.now()

                            if results.business_hr_bypass == "Y" and results.holiday_hour_bypass == "Y":
                                sla_due = sla_start + timedelta(minutes=int(results.response_time_sla))
                                print("done sla due normally")

                            else:
                                sla_due = calculate_sla(ticket_customer_id, sla_start, results.response_time_sla,
                                                        results.business_hr_bypass, results.holiday_hour_bypass)
                                print("done sla due by calculate sla method")

                            new_sla_log = SLALog(
                                customer_id=ticket_customer_id,
                                sub_customer_id=user_customer_id,
                                ticket_id=ticket_id,
                                sla_start=sla_start,
                                sla_due=sla_due,
                                ticket_status='open',
                                sla_status='not_breached',
                                created_at=sla_start,
                                sla_type="response_sla"
                            )
                            db.session.add(new_sla_log)
                            db.session.commit()


                        else:
                            print("Customer sla cannot start")
                        ### insert data into ticket transaction
                        new_transaction = TicketTransaction(
                            ticket_id=ticket_id,
                            customer_id=ticket_customer_id,
                            insert_date=datetime.now(),
                            level=0,
                            user_assigned_id=user_Assigned_Details.user_id,
                            group_assign_flag=False,
                            user_assign_flag=True,
                            file_paths=file_path
                        )
                        db.session.add(new_transaction)
                        db.session.commit()

                        ## add event logs
                        new_ticke_eventlog = TicketEventLog(
                            ticket_id=ticket_id,
                            event_description=f"User {username} assigned ticket to user {user_Assigned_Details.user_id}.",
                            event_datetime=datetime.now()
                        )
                        db.session.add(new_ticke_eventlog)
                        db.session.commit()

                        ## update bucket from ticket master
                        ticket = TicketMaster.query.get(ticket_id)
                        if ticket:
                            ticket.bucket = user_Assigned_Details.username
                            db.session.commit()

                        # assigned_user = User.query.filter_by(username=assign_to_user).first()
                        # recipient_emails = [assigned_user.email] if assigned_user else []

                        workflow_groups = db.session.query(Workflow.user_group_name).filter_by(
                            customer_id=ticket_customer_id).distinct().all()
                        workflow_groups = [group.user_group_name for group in workflow_groups]

                        # Step 2: Find all users belonging to these groups
                        assigned_users = (db.session.query(User.email)
                                                .join(UserGroups, User.user_id == UserGroups.user_id)
                                                .filter(UserGroups.user_group.in_(workflow_groups))
                                                .distinct().all())
                        recipient_emails = [user.email for user in assigned_users]

                        for i in recipient_emails:
                            print("user recipient: ", i)

                        if recipient_emails:
                            # Email subject and body (replace with your desired content)
                            subject = f"FW: [External] {ticket_customer_data.type} {ticket_id} | ASSIGNED | {assign_to_user}"
                            message_body = f"""
                                <!DOCTYPE html>
                                    <html>
                                    <head>
                                    <title>Ticket Assigned</title>
                                    </head>
                                    <body>
                                    <p>Hi,</p>

                                    <p>Your ticket-{ticket_id} has been assigned to user, he will soon pick it up.</p>

                                    <table style="border: 1px solid black; border-collapse: collapse;">
                                      <tr>
                                        <th style="border: 1px solid black; padding: 5px;">Notification Details</th>
                                        <th style="border: 1px solid black; padding: 5px;"></th>
                                      </tr>
                                      <tr>
                                        <td style="border: 1px solid black; padding: 5px;">Ticket No</td>
                                        <td style="border: 1px solid black; padding: 5px;">{ticket_id}</td>
                                      </tr>
                                      <tr>
                                        <td style="border: 1px solid black; padding: 5px;">Status</td>
                                        <td style="border: 1px solid black; padding: 5px;">Assigned</td>
                                      </tr>
                                      <tr>
                                        <td style="border: 1px solid black; padding: 5px;">Notification Date Time</td>
                                        <td style="border: 1px solid black; padding: 5px;">{datetime.now()}</td>
                                      </tr>
                                      <tr>
                                        <td style="border: 1px solid black; padding: 5px;">Severity</td>
                                        <td style="border: 1px solid black; padding: 5px;">{ticket.severity}</td>
                                      </tr>
                                      <tr>
                                        <td style="border: 1px solid black; padding: 5px;">Assigned User</td>
                                        <td style="border: 1px solid black; padding: 5px;">{assign_to_user}</td>
                                      </tr>
                                      <tr>
                                        <td style="border: 1px solid black; padding: 5px;">Description</td>
                                        <td style="border: 1px solid black; padding: 5px;">Your ticket-{ticket_id} has been assigned, {assign_to_user} will soon pick it up. Make your focus on resolutions.</td>
                                      </tr>
                                      <tr>
                                        <td style="border: 1px solid black; padding: 5px;">Resolution</td>
                                        <td style="border: 1px solid black; padding: 5px;">{ticket.remark}</td>
                                      </tr>
                                    </table>

                                    <p>Thanks,</p>
                                    <p>OTRS Support Team</p>
                                    </body>
                                    </html>
                                    """

                            # Use the `send_email_async` function you defined in `create_ticket.py`
                            send_user_email_async(recipient_emails, subject, message_body)

                        return jsonify({"msg": "Ticket assigned to user", "ticketId": ticket_id}), 201

                else:
                    return jsonify({"msg": "no user found"}), 401

            return jsonify({"msg": "Cannot assign ticket", "ticketId": ticket_id}), 201

        except Exception as e:
            print(e, "<<-----------------------")
            db.session.rollback()
            return jsonify({'message': 'Error assigning ticket', 'error': str(e)}), 500