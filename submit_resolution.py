import json
from datetime import datetime

import jwt
from flask import request, jsonify
from flask_cors import cross_origin
from flask_restful import Resource

from jwtData import token_required
from models import TicketMaster, TicketTransaction, TicketResolution, db, TicketEventLog

SECRETKEY = 'mysecretkey12345'


class SubmitResolution(Resource):
    @cross_origin()
    @token_required
    def get(self, ticket_id):
        return jsonify({'hello': ticket_id})

    @cross_origin()
    @token_required
    def post(self, ticket_id):
        print("..............")
        try:
            token = request.headers.get('Authorization')
            jwtData = jwt.decode(token, SECRETKEY, algorithms=['HS256'])
            data = request.get_json()
            print(ticket_id)
            user_customer_id = jwtData['customerid']
            user_id = jwtData['userid']
            username = jwtData['username']

            title = data.get('title')
            description = data.get('description')
            supporting_files = data.get('fileNames')
            print(supporting_files)

            file_path = ""

            for i in supporting_files:
                print(i)
                file_path += i + ", "

            file_path = file_path[:len(file_path) - 2]

            file_paths = "[" + file_path + "]"

            print("file_paths " + file_paths)

            ticketdata = TicketMaster.query.filter_by(ticket_id=ticket_id).first()
            ticket_customer_id = ticketdata.customer_id

            buckeet = TicketMaster.query.filter_by(ticket_id=ticket_id).first()
            print(buckeet.bucket, username)

            if not username == buckeet.bucket:
                return jsonify({"msg": "Ticket is not in your bucket.", "ticketId": ticket_id}), 201

            transaction_id_details = TicketTransaction.query.filter_by(ticket_id=ticket_id).order_by(
                TicketTransaction.id.desc()).first()

            transaction_id = transaction_id_details.id

            new_resolution = TicketResolution(
                ticket_id=ticket_id,
                insert_date=datetime.now(),
                customer_id=ticket_customer_id,
                transaction_id=transaction_id,
                title=title,
                description=description,
                resolution_by=user_id,
                supporting_files=file_paths
            )

            db.session.add(new_resolution)
            db.session.commit()

            new_ticke_eventlog = TicketEventLog(
                ticket_id=ticket_id,
                event_description=f"Resolution submited by {username}",
                event_datetime=datetime.now()
            )
            db.session.add(new_ticke_eventlog)
            db.session.commit()

            return jsonify({"message": "Resolution submited"}), 200



        except Exception as e:
            print(e, "<<-----------------------")
            return jsonify({'message': 'Error creating ticket', 'error': str(e)}), 500