from datetime import date, timedelta

import jwt
from flask import jsonify, request
from flask_cors import cross_origin
from flask_restful import Resource
from sqlalchemy import and_, func, desc

from jwtData import token_required
from models import TicketMaster, TicketFalseFlag, db


JWT_SECRET_KEY = "mysecretkey12345"


class TicketCounts(Resource):
    @cross_origin()
    @token_required
    def get(self):
        try:
            token = request.headers.get('Authorization')
            jwtdata = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])

            user_customer_id = jwtdata['customerid']

            today = date.today()

            # Construct the query based on user role and date filter
            if user_customer_id == 1:  # Admin
                query = TicketMaster.query.filter(
                    TicketMaster.raised_at >= today,
                    TicketMaster.raised_at <= today + timedelta(days=1)
                )
            else:
                query = TicketMaster.query.filter_by(
                    customer_id=user_customer_id
                ).filter(
                    TicketMaster.raised_at >= today,
                    TicketMaster.raised_at <= today + timedelta(days=1)
                )

            # Get closed ticket count
            closed_ticket_count = query.filter(TicketMaster.status == 'closed').count()

            # Get false flag count
            false_positive_count = (db.session.query(func.count(TicketMaster.ticket_id))
                                    .join(TicketFalseFlag, TicketMaster.ticket_id == TicketFalseFlag.ticketid)
                                    .filter(
                TicketFalseFlag.is_false == 1,
                TicketFalseFlag.date_time == (
                    db.session.query(func.max(TicketFalseFlag.date_time))
                    .filter(TicketFalseFlag.ticketid == TicketMaster.ticket_id)
                    .filter(TicketFalseFlag.date_time >= today)
                    .scalar_subquery()
                )
            ).scalar())

            false_flag_count = db.session.query(func.count(TicketMaster.ticket_id)).join(
                TicketFalseFlag, TicketMaster.ticket_id == TicketFalseFlag.ticketid
            ).filter(
                    TicketMaster.raised_at >= today,
                    TicketMaster.raised_at <= today + timedelta(days=1),
                    TicketFalseFlag.is_false == 1
            ).order_by(desc(TicketFalseFlag.date_time)).limit(1).scalar()



            # Handle case where no tickets are found
            if closed_ticket_count is None:
                closed_ticket_count = 0
            if false_flag_count is None:
                false_flag_count = 0

            return jsonify({
                "closed_ticket_count": closed_ticket_count,
                "false_flag_count": false_flag_count
            })

        except Exception as e:
            print(e, "<<-----------------------")
            db.session.rollback()
            return jsonify({'message': 'Error fetching ticket counts', 'error': str(e)}), 500