from datetime import datetime, timedelta
import jwt
from flask import jsonify, request
from flask_cors import cross_origin
from flask_restful import Resource, reqparse
from sqlalchemy import desc, func, and_, or_, extract
from sqlalchemy.orm import aliased
import json

from jwtData import token_required
from models import TicketMaster, CustomerMaster, TicketTransaction, SLALog, TicketFalseFlag, db

JWT_SECRET_KEY = 'mysecretkey12345'


class TicketFilters(Resource):
    @cross_origin()
    @token_required
    def post(self):

        token = request.headers.get('Authorization')
        jwtData = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
        user_customer_id = jwtData['customerid']
        user_group_name = jwtData.get('groupname')
        username = jwtData['username']

        print(request.get_json())

        data = request.get_json()
        args = data

        try:
            start_date = datetime.strptime(args['start_date'], '%Y-%m-%d')
            end_date = datetime.strptime(args['end_date'], '%Y-%m-%d') + timedelta(days=1)
        except ValueError:
            return json.dumps({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400

        # Handle missing start_time and end_time, set default to None if not provided
        start_time = None
        end_time = None

        if 'start_time' in args:
            try:
                start_time_str = args['start_time'] + ":00" if len(args['start_time']) == 5 else args['start_time']
                start_time = datetime.strptime(start_time_str, '%H:%M:%S').time()
                print("start time: ", start_time)
            except ValueError:
                return json.dumps({'error': 'Invalid time format for start_time. Use HH:MM or HH:MM:SS'}), 400

        if 'end_time' in args:
            try:
                end_time_str = args['end_time'] + ":00" if len(args['end_time']) == 5 else args['end_time']
                end_time = datetime.strptime(end_time_str, '%H:%M:%S').time()
                print("end time: ", end_time)
            except ValueError:
                return json.dumps({'error': 'Invalid time format for end_time. Use HH:MM or HH:MM:SS'}), 400

        allowed_sort_columns = [
            'ticket_id', 'customer_id', 'type', 'raised_at', 'title', 'description', 'severity',
            'priority', 'data', 'raised_by_id', 'bucket', 'status', 'resolved_by_id'
        ]

        if args['sort_by'] not in allowed_sort_columns:
            return json.dumps({'error': 'Invalid sort column'}), 400

        if args['sort_order'] not in ['asc', 'desc']:
            return json.dumps({'error': 'Invalid sort order'}), 400

        # Construct the query
        query = TicketMaster.query

        # Apply date filters
        query = query.filter(TicketMaster.raised_at >= start_date, TicketMaster.raised_at <= end_date)

        # Apply time filters if provided
        # if start_time and end_time:
        #     query = query.filter(
        #         and_(
        #             extract('hour', TicketMaster.raised_at) >= start_time.hour,
        #             extract('minute', TicketMaster.raised_at) >= start_time.minute,
        #             extract('second', TicketMaster.raised_at) >= start_time.second,
        #             extract('hour', TicketMaster.raised_at) <= end_time.hour,
        #             extract('minute', TicketMaster.raised_at) <= end_time.minute,
        #             extract('second', TicketMaster.raised_at) <= end_time.second
        #         )
        #     )
        if start_time and end_time:
            start_datetime = datetime.combine(start_date, start_time)
            end_datetime = datetime.combine(end_date, end_time)

            query = query.filter(
                and_(
                    TicketMaster.raised_at >= start_datetime,
                    TicketMaster.raised_at <= end_datetime
                )
            )

        # Apply other filters
        if int(user_customer_id) == 1:
            if args.get('customer_id'):
                query = query.filter(TicketMaster.customer_id == args['customer_id'])
        else:
            query = query.filter(TicketMaster.customer_id == user_customer_id)

        if args.get('ticket_id'):
            query = query.filter(TicketMaster.ticket_id == args['ticket_id'])
        # if args.get('type'):
        #        query = query.filter(TicketMaster.type == args['type'])
        if args.get('status'):
            query = query.filter(TicketMaster.status == args['status'])
        if args.get('priority'):
            query = query.filter(TicketMaster.priority == args['priority'])

        if args.get('raised_by_id'):
            query = query.filter(TicketMaster.raised_by_id == args['raised_by_id'])
        if args.get('resolved_by_id'):
            query = query.filter(TicketMaster.resolved_by_id == args['resolved_by_id'])
        if args.get('bucket'):
            query = query.filter(TicketMaster.bucket == args['bucket'])
        if args.get('title'):
            query = query.filter(TicketMaster.title == args['title'])

        # Subquery to get the latest record from TicketFalseFlag for each ticket based on date_time
        latest_flag_subquery = (
            db.session.query(TicketFalseFlag.ticketid, func.max(TicketFalseFlag.date_time).label('latest_flag_time'))
            .group_by(TicketFalseFlag.ticketid)
            .subquery()
        )

        # Alias for the TicketFalseFlag table to reference the latest record
        latest_flag = aliased(TicketFalseFlag)

        # Join the main query with the TicketFalseFlag table using ticketid
        query = query.join(
            latest_flag,
            TicketMaster.ticket_id == latest_flag.ticketid
        )

        # Ensure only the latest record for each ticket is used, matching the date_time from the subquery
        query = query.filter(
            latest_flag.date_time == latest_flag_subquery.c.latest_flag_time
        )

        # Apply the filter based on the 'type' argument
        if args.get('type'):
            if args['type'] == 'true':  # Fetch tickets where the latest record has is_false = 1 (true)
                query = query.filter(latest_flag.is_false == 1)

            elif args['type'] == 'false':  # Fetch tickets where the latest record has is_false = 0 (false)
                query = query.filter(latest_flag.is_false == 0)

        # Apply sorting
        if args['sort_order'] == 'asc':
            query = query.order_by(args['sort_by'])
        else:
            query = query.order_by(desc(args['sort_by']))

        tickets = query.all()

        # Process tickets and return the response
        ticket_data = []
        for record in tickets:
            customername = CustomerMaster.query.filter_by(customer_id=record.customer_id).first()

            ticket_details = {
                'ticket_id': record.ticket_id,
                'customer_id': record.customer_id,
                'customer_name': customername.customer_name if customername else None,
                'type': record.type,
                'raised_at': record.raised_at.strftime("%Y-%m-%d %H:%M:%S"),
                'title': record.title,
                'description': record.description,
                'severity': record.severity,
                'priority': record.priority,
                'data': record.remark,
                'raised_by_id': record.raised_by_id,
                'bucket': record.bucket,
                'status': record.status,
                'file_paths': '[]',
                'incident_id': record.tracking_id
            }

            latest_false_flag = TicketFalseFlag.query.filter_by(ticketid=record.ticket_id).order_by(
                desc(TicketFalseFlag.date_time)
            ).first()

            if latest_false_flag:
                ticket_details['false_positive'] = latest_false_flag.is_false  # Use actual value from latest entry
                ticket_details['latest_false_flag'] = {
                    'date_time': latest_false_flag.date_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'is_false': latest_false_flag.is_false
                }

            if user_customer_id == 1:
                print('userid---', 1)
                latest_ticket_transaction = TicketTransaction.query.filter_by(
                    ticket_id=record.ticket_id
                ).order_by(desc(TicketTransaction.insert_date)).first()
            else:
                print('userid else', record.ticket_id)
                latest_ticket_transaction = TicketTransaction.query.filter_by(
                    customer_id=user_customer_id,
                    ticket_id=record.ticket_id
                ).order_by(desc(TicketTransaction.insert_date)).first()

            if latest_ticket_transaction:
                if record.status == 'open' and latest_ticket_transaction.group_assign_flag == True and user_group_name == latest_ticket_transaction.group_assigned_name:
                    ticket_details['canPick'] = True
                else:
                    ticket_details['canPick'] = False

            "if role is admin then can_assign = Ture"
            ticket_details['canAssign'] = False

            ## check if ticket is assigned to me
            if username == record.bucket:
                ticket_details['assignedToMe'] = True
            else:
                ticket_details['assignedToMe'] = False

            latest_sla_log = SLALog.query.filter_by(ticket_id=record.ticket_id).order_by(SLALog.id.desc()).first()
            if latest_sla_log:
                current_time = datetime.now()
                breached_status = 'breached' if (
                            current_time > latest_sla_log.sla_due and record.status == 'open') else 'not breached'
                ticket_details['breach_status'] = breached_status
                ticket_details['sla_due'] = latest_sla_log.sla_due.strftime("%Y-%m-%d %H:%M:%S")

            ticket_data.append(ticket_details)

        return jsonify({'tickets': ticket_data})
