# import json
# from datetime import datetime, timedelta
#
# import jwt
# from flask import request, jsonify
# from flask_cors import cross_origin
# from flask_restful import Resource
# from sqlalchemy import desc
#
# from jwtData import token_required
# from models import TicketMaster, TicketTransaction, db, CustomerMaster, SLALog, TicketFalseFlag, User, RoleMaster
# from sqlalchemy import exc as sa_exc
#
# JWT_SECRET_KEY = 'mysecretkey12345'
#
#
# class Dashboard(Resource):
#
#     @cross_origin()
#     @token_required
#     def get(self):
#         return {'hello': 'hi'}
#
#     @cross_origin()
#     @token_required
#     def post(self):
#         print("..............")
#         try:
#             token = request.headers.get('Authorization')
#             # print("My TOKEN: ", token)
#             jwtdata = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
#
#             userid = jwtdata['userid']
#             user_group_name = jwtdata['groupname']
#             user_customer_id = jwtdata['customerid']
#             username = jwtdata['username']
#
#             role = User.query.filter_by(username=username).first()
#             user_role = role.role_id
#
#             role_table = RoleMaster.query.filter_by(role_id=user_role).first()
#             updated_role = role_table.role_name
#
#             print("user_Role", updated_role)
#
#             print("user customer id: ", user_customer_id)
#
#             "get the  ticket id and details "
#
#             today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
#             today_end = today_start + timedelta(days=1)
#             if user_customer_id == 1:
#                 records = TicketMaster.query.filter(
#                     TicketMaster.raised_at >= today_start,
#                     TicketMaster.raised_at <= today_end
#                 ).all()
#             else:
#                 records = TicketMaster.query.filter_by(customer_id=user_customer_id).filter(
#                     TicketMaster.raised_at >= today_start,
#                     TicketMaster.raised_at <= today_end
#                 ).all()
#
#             all_tickets = []
#
#             if not records:
#                 return json.dumps(
#                     {"msg": "successful", "ticketId": all_tickets, "username": username, "customerid": user_customer_id,
#                      'role': updated_role}), 201
#
#             for record in records:
#                 print("Record: ", record.ticket_id)
#                 customername = CustomerMaster.query.filter_by(customer_id=record.customer_id).first()
#                 severity = record.severity
#                 if severity == 'S1':
#                     severity = 'P1'
#                 elif severity == 'S2':
#                     severity = 'P2'
#                 elif severity == 'S3':
#                     severity = 'P3'
#                 elif severity == 'S4':
#                     severity = 'P4'
#
#                 ticket_details = {
#                     'ticket_id': record.ticket_id,
#                     'customer_id': record.customer_id,
#                     'customer_name': customername.customer_name,
#                     'type': record.type,
#                     'raised_at': record.raised_at.strftime("%Y-%m-%d %H:%M:%S"),
#                     'title': record.title,
#                     'description': record.description,
#                     'severity': severity,
#                     'priority': record.priority,
#                     'data': record.remark,
#                     'raised_by_id': record.raised_by_id,
#                     'bucket': record.bucket,
#                     'status': record.status,
#                     'file_paths': '[]'
#                 }
#
#                 # Get the latest false flag entry (if any)
#                 latest_false_flag = TicketFalseFlag.query.filter_by(ticketid=record.ticket_id).order_by(
#                     desc(TicketFalseFlag.date_time)
#                 ).first()
#
#                 # Determine false positive based on latest entry
#                 ticket_details['false_positive'] = False  # Initialize to False
#                 if latest_false_flag and latest_false_flag.is_false == 1:
#                     ticket_details['false_positive'] = True
#
                # ## get the latest record of ticket transaction
                # if user_customer_id == 1:
                #     latest_ticket_transaction = TicketTransaction.query.filter_by(
                #         ticket_id=record.ticket_id
                #     ).order_by(desc(TicketTransaction.insert_date)).first()
                # else:
                #     latest_ticket_transaction = TicketTransaction.query.filter_by(
                #         customer_id=user_customer_id,
                #         ticket_id=record.ticket_id
                #     ).order_by(desc(TicketTransaction.insert_date)).first()
                #
                # print("latest ticket is: ", latest_ticket_transaction.group_assign_flag)
#
                # if latest_ticket_transaction.group_assign_flag == None:
                #     continue
                #
                # if record.status == 'open' and latest_ticket_transaction.group_assign_flag == True and user_group_name == latest_ticket_transaction.group_assigned_name:
                #     ticket_details['canPick'] = True
                # else:
                #     ticket_details['canPick'] = False
                #
                # "if role is admin then can_assign = Ture"
#                 ticket_details['canAssign'] = False
#
#                 ## check if ticket is assigned to me
#                 if username == record.bucket:
#                     ticket_details['assignedToMe'] = True
#                 else:
#                     ticket_details['assignedToMe'] = False
#
#                 latest_sla_log = SLALog.query.filter_by(ticket_id=record.ticket_id).order_by(SLALog.id.desc()).first()
#                 if latest_sla_log:
#                     current_time = datetime.now()
#                     breached_status = 'breached' if (
#                             current_time > latest_sla_log.sla_due and record.status == 'open') else 'not breached'
#                     ticket_details['breach_status'] = breached_status
#                     ticket_details['sla_due'] = latest_sla_log.sla_due.strftime("%Y-%m-%d %H:%M:%S")
#                     ticket_details['sla_start'] = latest_sla_log.sla_start.strftime("%Y-%m-%d %H:%M:%S")
#
#                 all_tickets.append(ticket_details)
#
#             return json.dumps(
#                 {"msg": "successful", "ticketId": all_tickets, "username": username, "customerid": user_customer_id,
#                  'role': updated_role}), 201
#
#
#         except Exception as e:
#             print(e, "<<-----------------------")
#             db.session.rollback()
#             return json.dumps({'message': 'Error displaying ticket', 'error': str(e)}), 500


import json
from datetime import datetime, timedelta

import jwt
from flask import request, jsonify
from flask_cors import cross_origin
from flask_restful import Resource
from sqlalchemy import desc

from jwtData import token_required
from models import TicketMaster, TicketTransaction, db, CustomerMaster, SLALog, TicketFalseFlag, User, RoleMaster
from sqlalchemy import exc as sa_exc

JWT_SECRET_KEY = 'mysecretkey12345'


class Dashboard(Resource):

    @cross_origin()
    @token_required
    def get(self):
        return {'hello': 'hi'}

    @cross_origin()
    @token_required
    def post(self):
        print("..............")
        try:
            # Get the token and decode it
            token = request.headers.get('Authorization')
            jwtdata = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])

            userid = jwtdata['userid']
            user_group_name = jwtdata['groupname']
            user_customer_id = jwtdata['customerid']
            username = jwtdata['username']

            # Get user's role
            role = User.query.filter_by(username=username).first()
            user_role = role.role_id
            role_table = RoleMaster.query.filter_by(role_id=user_role).first()
            updated_role = role_table.role_name

            print("user_Role", updated_role)
            print("user customer id: ", user_customer_id)

            # Get page and per_page parameters from the request (for pagination)
            page = request.args.get('page', 1, type=int)  # Default to page 1
            per_page = request.args.get('per_page', 10, type=int)  # Default to 10 records per page

            # Construct the filter query based on user_customer_id
            query = TicketMaster.query

            today = datetime.now().date()
            raised_today_count = query.filter(TicketMaster.raised_at >= today).count()

            print("today raised tickets: ", raised_today_count)

            if user_customer_id != 1:
                query = query.filter_by(customer_id=user_customer_id)

            # Order by the most recent ticket (raised_at descending) and paginate
            records = query.order_by(desc(TicketMaster.raised_at)).limit(per_page).offset((page - 1) * per_page).all()

            all_tickets = []

            print("currentPage=", page, " perPage=", per_page)

            if not records:
                return jsonify(
                    {"msg": "successful", "ticketId": all_tickets, "username": username, "customerid": user_customer_id,
                     'role': updated_role, "currentPage": page, "perPage": per_page,
                     "raised_today": raised_today_count}), 201

            # Process the records
            for record in records:
                ticket_details = self._get_ticket_details(record, username, user_group_name, user_customer_id,
                                                          updated_role)
                all_tickets.append(ticket_details)

            return jsonify(
                {"msg": "successful", "ticketId": all_tickets, "username": username, "customerid": user_customer_id,
                 'role': updated_role, "currentPage": page, "perPage": per_page,
                 "raised_today": raised_today_count}), 201

        except Exception as e:
            print(e, "<<-----------------------")
            db.session.rollback()
            return jsonify({'message': 'Error displaying ticket', 'error': str(e)}), 500

    def _get_ticket_details(self, record, username, user_group_name, user_customer_id, updated_role):
        """Helper method to extract ticket details and determine flags for pagination."""
        # Get customer name for the ticket
        customername = CustomerMaster.query.filter_by(customer_id=record.customer_id).first()
        severity = record.severity
        if severity == 'S1':
            severity = 'P1'
        elif severity == 'S2':
            severity = 'P2'
        elif severity == 'S3':
            severity = 'P3'
        elif severity == 'S4':
            severity = 'P4'

        ticket_details = {
            'ticket_id': record.ticket_id,
            'customer_id': record.customer_id,
            'customer_name': customername.customer_name,
            'type': record.type,
            'raised_at': record.raised_at.strftime("%Y-%m-%d %H:%M:%S"),
            'title': record.title,
            'description': record.description,
            'severity': severity,
            'priority': record.priority,
            'data': record.remark,
            'raised_by_id': record.raised_by_id,
            'bucket': record.bucket,
            'status': record.status,
            'file_paths': '[]',
            'alert_id': record.alert_id,
            'incident_id': record.tracking_id
        }

        # Get the latest false flag entry (if any)
        latest_false_flag = TicketFalseFlag.query.filter_by(ticketid=record.ticket_id).order_by(
            desc(TicketFalseFlag.date_time)
        ).first()

        # Determine false positive based on latest entry
        ticket_details['false_positive'] = False  # Initialize to False
        if latest_false_flag and latest_false_flag.is_false == 1:
            ticket_details['false_positive'] = True

        ## get the latest record of ticket transaction
        if user_customer_id == 1:
            latest_ticket_transaction = TicketTransaction.query.filter_by(
                ticket_id=record.ticket_id
            ).order_by(desc(TicketTransaction.insert_date)).first()
        else:
            latest_ticket_transaction = TicketTransaction.query.filter_by(
                customer_id=user_customer_id,
                ticket_id=record.ticket_id
            ).order_by(desc(TicketTransaction.insert_date)).first()

        print("latest ticket is: ", latest_ticket_transaction.group_assign_flag)

        if latest_ticket_transaction and latest_ticket_transaction.group_assign_flag is not None:
            ticket_details[
                'canPick'] = True if record.status == 'open' and latest_ticket_transaction.group_assign_flag and user_group_name == latest_ticket_transaction.group_assigned_name else False
        else:
            ticket_details['canPick'] = False

            # if role is admin then can_assign = True
        ticket_details['canAssign'] = False if updated_role != "admin" else True

        # Check if user is assigned the ticket
        ticket_details['assignedToMe'] = True if username == record.bucket else False

        latest_sla_log = SLALog.query.filter_by(ticket_id=record.ticket_id).order_by(SLALog.id.desc()).first()
        if latest_sla_log:
            current_time = datetime.now()
            breached_status = 'breached' if current_time > latest_sla_log.sla_due and record.status == 'open' else 'not breached'
            ticket_details['breach_status'] = breached_status
            ticket_details['sla_due'] = latest_sla_log.sla_due.strftime("%Y-%m-%d %H:%M:%S")
            ticket_details['sla_start'] = latest_sla_log.sla_start.strftime("%Y-%m-%d %H:%M:%S")

        return ticket_details
