import json
import os

import jwt
from flask import request, send_file, jsonify, Response, Flask, send_from_directory
from flask_cors import cross_origin
from flask_restful import Resource

from jwtData import token_required
from models import TicketResolution, TicketMaster
from dotenv import load_dotenv

load_dotenv()

SECRETKEY = 'mysecretkey12345'


class DownloadDoc(Resource):
    @cross_origin()
    @token_required
    def get(self, document_name):
        return {'hello': document_name}

    @cross_origin()
    @token_required
    def post(self, document_name, ticket_id):
        print("..............")
        try:
            token = request.headers.get('Authorization')
            jwtData = jwt.decode(token, SECRETKEY, algorithms=['HS256'])
            # data = request.get_json()
            print("document_name: ", document_name)
            print(type(document_name))
            user_customer_id = jwtData['customerid']  # get from @token

            try:
                ticket_id = int(ticket_id)
            except ValueError:
                return json.dumps({"message": "Invalid ticket_id"}), 400

            # Fetch ticket details using ticket_id
            ticket = TicketMaster.query.filter_by(ticket_id=ticket_id).first()
            if not ticket:
                return json.dumps({"message": "Ticket not found"}), 404

            # Format creation date as YYYY-MM-DD (folder name)
            ticket_date_folder = ticket.raised_at.strftime('%Y-%m-%d')
            folder_path = os.path.join(os.getenv('UPLOAD_FOLDER'), ticket_date_folder)

            # if user_customer_id == 1:
            #     results = TicketResolution.query.filter(TicketResolution.supporting_files.like(f'%{document_name}%')).first()
            #     print(results)
            # else:
            #     results = TicketResolution.query.filter(
            #         (TicketResolution.customer_id == user_customer_id),
            #         TicketResolution.supporting_files.like(f'%{document_name}%')
            #     ).first()

            document_name = document_name.replace("[", "").replace("]", "")
            document_name = document_name.split(',')
            print(document_name)

            if document_name:
                for document in document_name:
                    print(folder_path)
                    file_path = os.path.join(folder_path, document)
                    print("Checking path: ", file_path)

                    # Extract the original filename by removing the unique ID
                    original_filename = "_".join(document.split("_")[1:])
                    print("original file name: ", original_filename)

                    if os.path.exists(file_path):
                        print("path exist: ", file_path)
                        return send_file(file_path, as_attachment=True, download_name=original_filename)

            return json.dumps({"message": "File not exist"}), 404

        except Exception as e:
            print(e, "<<-----------------------")
            return json.dumps({'message': 'Error creating ticket', 'error': str(e)}), 500