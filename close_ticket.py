import json
from dotenv import load_dotenv
import os
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from threading import Thread

import jwt
from flask import request, jsonify
from flask_cors import cross_origin
from flask_restful import Resource
from sqlalchemy import join

from jwtData import token_required
from models import TicketMaster, TicketEventLog, db, SLALog, User, UserGroups, Workflow

SECRETKEY = 'mysecretkey12345'


def send_email_async(recipient, subject, message_body):
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
                smtp_server = os.getenv('SMTP_SERVER')
                smtp_port = int(os.getenv('SMTP_PORT'))
                smtp_username = os.getenv('SMTP_USERNAME')
                smtp_password = os.getenv('SMTP_PASSWORD')

                try:
                    with smtplib.SMTP(smtp_server, smtp_port) as server:
                        server.starttls()
                        server.login(smtp_username, smtp_password)
                        # server.sendmail(sender, [recipient, cc], msg.as_string())
                        server.sendmail(sender, recipient, msg.as_string())
                        print("Email sent successfully.")
                except Exception as e:
                    print("Failed to send email:", str(e))

        email_thread = Thread(target=send_email)
        email_thread.start()


class CloseTicket(Resource):
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

            token = request.headers.get('Authorization')
            jwtData = jwt.decode(token, SECRETKEY, algorithms=['HS256'])
            # data = request.get_json()
            # print(data ,"<-----------------")
            user_customer_id = jwtData['customerid']
            userid = jwtData['userid']
            user_group_name = jwtData['groupname']
            username = jwtData['username']

            TicketDetails = TicketMaster.query.filter_by(ticket_id=ticket_id).first()
            ticket_customer_id = TicketDetails.customer_id

            ## get the ticket details
            ## check ticket master bucket == username of current user

            buckeet = TicketMaster.query.filter_by(ticket_id=ticket_id).first()
            print(buckeet.bucket, username)

            if not username == buckeet.bucket:
                return jsonify({"msg": "Ticket is not in your bucket.", "ticketId": ticket_id}), 201

            if buckeet.status == 'closed':
                return jsonify({"msg": "Ticket is already closed", "ticketId": ticket_id}), 201

            "check if user have authority to close ticket..."

            print("user group name", user_group_name)

            workflowDetails = Workflow.query.filter_by(user_group_name=user_group_name).first()
            print(workflowDetails.can_close)
            ticket = TicketMaster.query.get(ticket_id)
            if ticket and workflowDetails.can_close == "Y":
                ticket.status = 'closed'
                db.session.commit()
            else:
                return jsonify({"msg": "You cannot close the ticket"}), 403

            # update event log
            new_ticke_eventlog = TicketEventLog(
                ticket_id=ticket_id,
                event_description=f"Ticket closed by {username}.",
                event_datetime=datetime.now()
            )
            db.session.add(new_ticke_eventlog)
            db.session.commit()

            # close SLA
            latest_sla_log = SLALog.query.filter_by(ticket_id=ticket_id).order_by(SLALog.id.desc()).first()
            if latest_sla_log:
                current_time = datetime.now()
                breached_status = 'breached' if (
                            current_time > latest_sla_log.sla_due and latest_sla_log.ticket_status == 'open') else 'not breached'
                sla_log = SLALog.query.filter_by(id=latest_sla_log.id).first()
                if sla_log:
                    sla_log.sla_status = breached_status
                    sla_log.ticket_status = 'closed'
                    db.session.commit()

            # # Get recipient emails
            # recipient_emails = [User.query.filter_by(user_id=TicketDetails.raised_by_id).first().email]
            #
            # L1_users = db.session.query(User).select_from(
            #     join(User, UserGroups, User.user_id == UserGroups.user_id)
            # ).filter(
            #     UserGroups.user_group == 'L1',
            #     UserGroups.customer_id == ticket_customer_id
            # ).distinct(User.user_id).all()
            # for i in L1_users:
            #     if i.email not in recipient_emails:
            #         # print("l1 user email: ", i.email)
            #         recipient_emails.append(i.email)
            # # for i in recipient_emails:
            # #     print(i)
            #
            # # If the bucket is a group name, get the email addresses of all users in the group
            # if TicketDetails.bucket == 'L1' or TicketDetails.bucket == 'L2' or TicketDetails.bucket == 'L3':
            #     group_users = db.session.query(User).select_from(
            #         join(User, UserGroups, User.user_id == UserGroups.user_id)).filter(
            #         UserGroups.user_group == TicketDetails.bucket,
            #         UserGroups.customer_id == ticket_customer_id
            #     ).all()
            #     for user in group_users:
            #         if user.email not in recipient_emails:
            #             # print("group user: ", user.email)
            #             recipient_emails.append(user.email)
            #
            # # If the bucket is a username, get the email address of the user
            # else:
            #     assigned_user = User.query.filter_by(username=TicketDetails.bucket).first()
            #     if assigned_user:
            #         if assigned_user.email not in recipient_emails:
            #             # print("assigned user: ", assigned_user.email)
            #             recipient_emails.append(assigned_user.email)
            #
            # # print(recipient_emails)

            workflow_groups = db.session.query(Workflow.user_group_name).filter_by(
                customer_id=ticket_customer_id).distinct().all()
            workflow_groups = [group.user_group_name for group in workflow_groups]

            # Step 2: Find all users belonging to these groups
            assigned_users = (db.session.query(User.email)
                              .join(UserGroups, User.user_id == UserGroups.user_id)
                              .filter(UserGroups.user_group.in_(workflow_groups))
                              .distinct().all())
            recipient_emails = [user.email for user in assigned_users]

            if recipient_emails:
                # Email subject and body (replace with your desired content)
                subject = f"FW: [External] {ticket.type} {ticket_id} | CLOSED | {username}"
                message_body = f"""
                                <!DOCTYPE html>
                                    <html>
                                    <head>
                                    <title>Ticket Closed</title>
                                    </head>
                                    <body>
                                    <p>Hi,</p>

                                    <p>Your ticket-{ticket_id} has been closed.</p>

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
                                        <td style="border: 1px solid black; padding: 5px;">Closed</td>
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
                                        <td style="border: 1px solid black; padding: 5px;">Closed By</td>
                                        <td style="border: 1px solid black; padding: 5px;">{username}</td>
                                      </tr>
                                      <tr>
                                        <td style="border: 1px solid black; padding: 5px;">Description</td>
                                        <td style="border: 1px solid black; padding: 5px;">Your ticket-{ticket_id} has been closed by {username}. All necessary resolutions are given in Resolutions section.</td>
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
                send_email_async(recipient_emails, subject, message_body)

            return jsonify({"message": "Ticket closed"}), 200

        except Exception as e:
            print(e, "<<-----------------------")
            return jsonify({'message': 'Error closing ticket', 'error': str(e)}), 500