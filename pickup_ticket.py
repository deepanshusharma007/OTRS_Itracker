import json
from datetime import datetime, timedelta

import jwt
from flask import request, jsonify
from flask_cors import cross_origin
from flask_restful import Resource
from sqlalchemy import *
from sla_calculator import calculate_sla
from jwtData import token_required
from models import TicketTransaction, db, TicketMaster, TicketEventLog, SLAMaster, SLALog, Workflow

JWT_SECRET_KEY = "mysecretkey12345"


class TicketPickup(Resource):
    @cross_origin()
    @token_required
    def get(self):
        return {'hello': 'hi'}

    @cross_origin()
    @token_required
    def post(self, ticket_id):
        print("..............")
        try:
            token = request.headers.get('Authorization')
            jwtdata = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
            # data = request.get_json()
            # print(data, "<-----------------")
            user_customer_id = jwtdata['customerid']
            userid = jwtdata['userid']
            user_group_name = jwtdata['groupname']
            ticketid = ticket_id
            username = jwtdata['username']

            user_workflow_data = Workflow.query.filter_by(customer_id=user_customer_id,
                                                          user_group_name=user_group_name).first()
            if user_workflow_data.can_pickup == 'N':
                return jsonify({'msg': 'You are not permitted to pickup the ticket'}), 404

            ticket_customer_data = TicketMaster.query.filter_by(ticket_id=ticketid).first()
            ticket_customer_id = ticket_customer_data.customer_id

            "get the  ticket id and details "
            latest_ticket_transaction = TicketTransaction.query.filter_by(
                ticket_id=ticket_id
            ).order_by(desc(TicketTransaction.insert_date)).first()

            print("Testing")

            if latest_ticket_transaction.group_assign_flag == True and user_group_name == latest_ticket_transaction.group_assigned_name:
                "add a record to ticket transaction"
                "Update the status on ticket master bucket - username  status - open"
                "Update ticket event logs"
                "Update SLA log table update previous data as not breached or breached  and add new SAL calculation"

                ## insert into ticket transaction
                print("Andar aa gya..............")
                new_transaction = TicketTransaction(
                    ticket_id=ticket_id,
                    customer_id=ticket_customer_id,
                    insert_date=datetime.now(),
                    level=latest_ticket_transaction.level + 1,
                    group_assigned_name=user_group_name,
                    user_assigned_id=userid,
                    group_assign_flag=False,
                    user_assign_flag=True,
                    file_paths="[]"
                )
                db.session.add(new_transaction)
                db.session.commit()
                print("transaction updated")
                ## update bucket details

                ticket = TicketMaster.query.filter_by(ticket_id=ticket_id).first()
                if ticket:
                    ticket.bucket = username
                    db.session.commit()
                print("ticket updated")
                ## update ticket event log

                new_ticke_eventlog = TicketEventLog(
                    ticket_id=ticket_id,
                    event_description=f"Ticket picked up by user {username}.",
                    event_datetime=datetime.now()
                )
                db.session.add(new_ticke_eventlog)
                db.session.commit()
                print("eventlog updated")

                ## update SLA log
                "get the customer id of userid"

                record = SLALog.query.filter_by(ticket_id=ticket_id).order_by(SLALog.id.desc()).first()

                if not record:
                    pass
                elif record:
                    if record.sub_customer_id == user_customer_id and record.sla_type == 'response_sla':
                        print("condition 1 got true")
                        records = SLAMaster.query.filter_by(customer_id=ticket_customer_id,
                                                            sub_customer_id=user_customer_id,
                                                            severity=ticket_customer_data.severity,
                                                            ticket_type=ticket_customer_data.type).first()

                        print("SLA->", records.resolve_time_sla)

                        sla_start = datetime.now()
                        print("sla started for condition 1: ", sla_start)

                        if records.business_hr_bypass == "Y" and records.holiday_hour_bypass == "Y":
                            sla_due = sla_start + timedelta(minutes=int(records.resolve_time_sla))
                            print("done sla due normally")

                        else:
                            sla_due = calculate_sla(ticket_customer_id, sla_start, records.resolve_time_sla,
                                                    records.business_hr_bypass, records.holiday_hour_bypass)
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
                            sla_type="resolution_sla"
                        )

                        db.session.add(new_sla_log)
                        db.session.commit()


                    elif record.sub_customer_id == user_customer_id and record.sla_type == 'resolution_sla':
                        print("passing the sla")
                        pass

                    elif record.sub_customer_id != user_customer_id and record.sla_type == 'response_sla':
                        print("condition 2 got true")
                        # update the SLA record row with breach or not breach
                        records = SLAMaster.query.filter_by(customer_id=ticket_customer_id,
                                                            sub_customer_id=user_customer_id,
                                                            severity=ticket_customer_data.severity,
                                                            ticket_type=ticket_customer_data.type).first()

                        print("SLA->", records.resolve_time_sla)

                        sla_start = datetime.now()
                        print("sla started for condition 2 start", sla_start)

                        if records.business_hr_bypass == "Y" and records.holiday_hour_bypass == "Y":
                            sla_due = sla_start + timedelta(minutes=int(records.resolve_time_sla))
                            print("done sla due normally")

                        else:
                            sla_due = calculate_sla(ticket_customer_id, sla_start, records.resolve_time_sla,
                                                    records.business_hr_bypass, records.holiday_hour_bypass)
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
                                sla_type="resolution_sla"
                            )

                            db.session.add(new_sla_log)
                            db.session.commit()
                return json.dumps({"msg": "Ticket picked up", "ticketId": ticket_id}), 201
            else:
                return json.dumps({"msg": "Cannot assign ticket", "ticketId": ticket_id}), 201

        except Exception as e:
            print(e, "<<-----------------------")
            db.session.rollback()
            return json.dumps({'message': 'Error picking ticket', 'error': str(e)}), 500
