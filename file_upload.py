import json
import os
import uuid

from flask import request, jsonify
from flask_cors import cross_origin
from flask_restful import Resource
from datetime import datetime

from jwtData import token_required
from models import db
from dotenv import load_dotenv

load_dotenv()

## upload files
class FileUpload(Resource):
    @cross_origin()
    @token_required
    def get(self):
        return {'hello' :'hi'}

    @cross_origin()
    @token_required
    def post(self):
        print("..............")
        try:
            print('hi')
            if 'file' not in request.files:
                return json.dumps({'error': 'No file part'}), 400

            file = request.files['file']
            if file.filename == '':
                return json.dumps({'error': 'No selected file'}), 400

            # Get today's date for folder naming
            today_date = datetime.now().strftime('%Y-%m-%d')
            date_folder_path = os.path.join(os.getenv('UPLOAD_FOLDER'), today_date)
            os.makedirs(date_folder_path, exist_ok=True)  # Create folder if it doesn't exist

            # Generate unique filename
            unique_id = uuid.uuid4()
            filename = file.filename
            new_filename = f"{unique_id}_{filename}"

            # Save file in the date folder
            file_path = os.path.join(date_folder_path, new_filename)
            file.save(file_path)

            response = {
                'filename': filename,
                'new_filename': str(unique_id) + '_' + filename,
                'file_path': file_path,
                'message': 'File successfully uploaded and saved'
            }

            return json.dumps(response)
        except Exception as e:
            print(e ,"<<-----------------------")
            db.session.rollback()
            return json.dumps({'message': 'Error creating ticket', 'error': str(e)}), 500