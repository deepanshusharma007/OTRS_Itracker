## Ticket Details
import datetime
import json
from ast import literal_eval

import jwt
from flask import request, jsonify
from flask_cors import cross_origin
from flask_restful import Resource

from jwtData import token_required
from models import TicketMaster, SLALog, db, CustomerMaster, TicketTransaction, TicketEventLog, TicketResolution, User, \
    TicketFalseFlag, RoleMaster
from sqlalchemy import exc as sa_exc, desc

JWT_SECRET_KEY = 'mysecretkey12345'


class TicketDetails(Resource):
    @cross_origin()
    @token_required
    def get(self, ticket_id):
        return {'hello': ticket_id}

    @cross_origin()
    @token_required
    def post(self, ticket_id):
        # print("..............")
        try:
            token = request.headers.get('Authorization')
            # print("My TOKEN: ", token)
            jwtdata = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])

            # data = request.get_json()
            # print(ticket_id)
            user_customer_id = jwtdata['customerid']
            user_group_name = jwtdata['groupname']
            username = jwtdata['username']

            # Get user's role
            role = User.query.filter_by(username=username).first()
            user_role = role.role_id
            role_table = RoleMaster.query.filter_by(role_id=user_role).first()
            updated_role = role_table.role_name

            ## check ticket customer id
            ## check user customer id == ticket customer id or 1

            record = TicketMaster.query.filter_by(ticket_id=ticket_id).first()
            if record != None:
                if user_customer_id == 1 or user_customer_id == record.customer_id:
                    if record.file_paths:
                        try:
                            # supporting_files_list = literal_eval(record.file_paths)
                            supporting_files_list = record.file_paths
                            print(record.file_paths)
                            supporting_files_list = supporting_files_list.strip('[]')
                            cleaned_string = supporting_files_list

                            # Step 2: Split the string by ', ' to get individual filenames
                            file_array = supporting_files_list.split(', ')

                            # Print the resulting array of strings
                            print("file array: ", file_array)

                            supporting_files_list = file_array


                        except (ValueError, SyntaxError):
                            supporting_files_list = [record.file_paths]
                    print("inside master: ", supporting_files_list)

                    # Fetch customer name
                    customer = CustomerMaster.query.filter_by(customer_id=record.customer_id).first()
                    customer_name = customer.customer_name if customer else "None"

                    # Fetch raised by name (Assuming raised_by_id stores user ID)
                    raised_by = User.query.filter_by(user_id=record.raised_by_id).first()
                    raised_by_name = raised_by.username if raised_by else "None"

                    severity = record.severity
                    if severity == "S1":
                        severity = "P1"
                    elif severity == "S2":
                        severity = "P2"
                    elif severity == "S3":
                        severity = "P3"
                    elif severity == "S4":
                        severity = "P4"

                    ticket_details = {
                        'ticket_id': record.ticket_id,
                        'customer_id': record.customer_id,
                        'type': record.type,
                        'raised_at': record.raised_at.strftime("%Y-%m-%d %H:%M:%S"),
                        'title': record.title,
                        'description': record.description,
                        'data': record.remark,
                        'raised_by_id': record.raised_by_id,
                        'bucket': record.bucket,
                        'status': record.status,
                        'severity': severity,
                        'file_paths': supporting_files_list,
                        'alert_id': record.alert_id,
                        'incident_id': record.tracking_id
                        ## add breach status
                        ## add due
                    }

                    ticket_details['role'] = updated_role

                    raised_by = User.query.filter_by(user_id=ticket_details['raised_by_id']).first()
                    ticket_details['raised_by_name'] = raised_by.username
                    print("raised_by_name: ", raised_by.username)
                    # customer_name = CustomerMaster.query.filter_by(customer_id=user_customer_id).first()
                    ticket_details['customer_name'] = customer_name
                    print("customer name: ", customer_name)

                    latest_sla_log = SLALog.query.filter_by(ticket_id=ticket_id).order_by(SLALog.id.desc()).first()
                    if latest_sla_log:
                        current_time = datetime.datetime.now()
                        breached_status = 'breached' if (
                                current_time > latest_sla_log.sla_due and record.status == 'open') else 'not breached'
                        ticket_details['breach_status'] = breached_status
                        ticket_details['sla_due'] = latest_sla_log.sla_due.strftime("%Y-%m-%d %H:%M:%S")

                    ## assigned by ------------------------------------------------------------
                    ## get the ticket details from ticket transaction table and get details of that id
                    # latest_ticket_tr = TicketTransaction.query.filter_by(ticket_id=ticket_id).order_by(TicketTransaction.id.desc()).all()
                    # if len(latest_ticket_tr) >= 2:
                    #     print("length is greater..")
                    #     if latest_ticket_tr[1].group_assign_flag:
                    #         print(latest_ticket_tr[1].group_assigned_name)
                    #         ## get the group details with customer id
                    #     elif latest_ticket_tr[1].user_assign_flag:
                    #         print(latest_ticket_tr[1].user_assign_id)

                    ## Get resolution list-------------------------------------------------------------

                    print("--------------------------resolutions----------------------------")

                    resolutions = TicketResolution.query.filter_by(ticket_id=ticket_id).order_by(
                        TicketResolution.id.asc()).all()
                    if resolutions != None:
                        results = []
                        for resolution in resolutions:
                            # supporting_files_list = []
                            print(resolutions)
                            print("inside resolutions: ", resolution.supporting_files)
                            if resolution.supporting_files:
                                try:
                                    print(resolution.supporting_files)
                                    supporting_files_list = resolution.supporting_files.strip('[]')
                                    cleaned_string = supporting_files_list

                                    # Step 2: Split the string by ', ' to get individual filenames
                                    file_array = supporting_files_list.split(', ')

                                    # Print the resulting array of strings
                                    print("file array: ", file_array)

                                    supporting_files_list = file_array

                                except (ValueError, SyntaxError):
                                    print(resolution.supporting_files)
                                    supporting_files_list = resolution.supporting_files.strip('[]')
                                    cleaned_string = supporting_files_list

                                    # Step 2: Split the string by ', ' to get individual filenames
                                    file_array = supporting_files_list.split(', ')

                                    # Print the resulting array of strings
                                    print("file array: ", file_array)

                                    supporting_files_list = file_array

                            print("supporting_files_list: ", supporting_files_list)

                            print("resolution by: ", resolution.resolution_by)

                            resolved_by = User.query.filter_by(user_id=resolution.resolution_by).first()
                            if not resolved_by:
                                resolved_by = "---"
                            else:
                                resolved_by = resolved_by.username

                            print(resolved_by)

                            results.append({
                                'id': resolution.id,
                                'ticket_id': resolution.ticket_id,
                                'insert_date': resolution.insert_date.strftime("%Y-%m-%d %H:%M:%S"),
                                'customer_id': resolution.customer_id,
                                'transaction_id': resolution.transaction_id,
                                'title': resolution.title,
                                'description': resolution.description,
                                'resolution_by': resolution.resolution_by,
                                'resolved_by': resolved_by,
                                'supporting_files': supporting_files_list,
                                'remark': record.remark
                            })

                        ticket_details['resolutions'] = results

                    ## get Event logs

                    events = TicketEventLog.query.filter_by(ticket_id=ticket_id).order_by(TicketEventLog.id.asc()).all()
                    if events != None:
                        results = []
                        for event in events:
                            results.append({
                                'id': event.id,
                                'ticket_id': event.ticket_id,
                                'event_description': event.event_description,
                                'event_datetime': event.event_datetime.strftime("%Y-%m-%d %H:%M:%S")
                            })
                        ticket_details['eventLog'] = results

                    ## get SLA logs

                    sla_logs = SLALog.query.filter_by(ticket_id=ticket_id).all()
                    if sla_logs != None:
                        sla_data = []
                        for log in sla_logs:
                            sla_data.append({
                                'sla_start': log.sla_start.strftime("%Y-%m-%d %H:%M:%S"),
                                'sla_due': log.sla_due.strftime("%Y-%m-%d %H:%M:%S"),
                                'sla_status': log.sla_status,
                                'sla_type': log.sla_type
                            })
                        ticket_details['slaLogs'] = sla_data

                    ## can pick
                    ## get the latest record of ticket transaction
                    if user_customer_id == 1:
                        latest_ticket_transaction = TicketTransaction.query.filter_by(
                            ticket_id=ticket_id
                        ).order_by(desc(TicketTransaction.insert_date)).first()
                    else:
                        latest_ticket_transaction = TicketTransaction.query.filter_by(
                            customer_id=user_customer_id,
                            ticket_id=record.ticket_id
                        ).order_by(desc(TicketTransaction.insert_date)).first()

                    if record.status == 'open' and latest_ticket_transaction.group_assign_flag == True and user_group_name == latest_ticket_transaction.group_assigned_name:
                        print("true")
                        ticket_details['canPick'] = True
                    else:
                        print("false")
                        ticket_details['canPick'] = False

                    ticket_details['username'] = jwtdata['username']

                    false_positive = TicketFalseFlag.query.filter_by(ticketid=ticket_id).order_by(
                        TicketFalseFlag.srno.desc()).first()
                    if false_positive and false_positive.is_false == True:
                        ticket_details['isFalse'] = True
                    else:
                        ticket_details['isFalse'] = False

                    return ticket_details, 201

                else:
                    return jsonify({"message": "You are not allowed to access this ticket"})
            else:
                return jsonify({"message": "Ticket not found"})

        except Exception as e:
            print(e, "<<-----------------------")
            db.session.rollback()
            return jsonify({'message': 'Error creating ticket', 'error': str(e)}), 500

        # except sa_exc.SQLAlchemyError as e:
        # db.session.rollback()  # Rollback transaction
        # return jsonify({'error': 'Database error', 'details': str(e)}), 500

        # except (jwt.ExpiredSignatureError, jwt.InvalidTokenError) as e:
        # return jsonify({'error': 'Invalid or expired token'}), 401
