from io import StringIO, BytesIO

from flask_cors import cross_origin
from flask_restful import Resource
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors

from flask import request, jsonify, send_file

from jwtData import token_required
from models import TicketMaster, TicketResolution, SLALog, TicketEventLog


# ... other imports ...

def generate_ticket_csv(ticket_data, ticket_resolutions, logs):
    """
    Generates a CSV string containing ticket details, resolutions, and logs.
    """
    output = StringIO()

    # Write header row
    output.write(
        "Ticket ID,Title,Raised At,Description,Remark,Severity,Priority,Raised By Id,Updated At,Bucket,Status,File Paths\n")

    # Write ticket master data
    output.write(
        f"{ticket_data.ticket_id},{ticket_data.title},{ticket_data.raised_at},{ticket_data.description},{ticket_data.remark},{ticket_data.severity},{ticket_data.priority},{ticket_data.raised_by_id},{ticket_data.updated_at},{ticket_data.bucket},{ticket_data.status},{ticket_data.file_paths}\n")

    # Write ticket resolution data (one line per resolution)
    if ticket_resolutions:
        output.write("\nTicket Resolutions:\n")
        for resolution in ticket_resolutions:
            output.write(f"Resolution Description: {resolution.description}\n")
            output.write(f"Supporting Files: {resolution.supporting_files if resolution else 'N/A'}\n\n")

    # Write SLA log data (one line per log)
    if logs:
        output.write("\nAudit Logs:\n")
        for log in logs:
            output.write(f"Event Description: {log.event_description}\n")
            output.write(f"Event DateTime: {log.event_datetime}\n\n")

    return output.getvalue()


class ExportTicket(Resource):
    @cross_origin()
    @token_required
    def get(self, ticket_id):
        try:
            # Log the start of the function to make sure it is reached
            print("Fetching ticket data...")

            # Fetch ticket data from the database
            ticket_data = TicketMaster.query.filter_by(ticket_id=ticket_id).first()
            print(f"ticket_id: {ticket_id}, ticket_data: {ticket_data}")

            # Check if ticket_data exists, and handle the case where it doesn't
            if not ticket_data:
                print("No ticket data found.")
                return jsonify({'error': 'Ticket not found'}), 404

            print("Ticket data found, fetching resolutions and logs...")

            # Fetch ticket resolution data
            ticket_resolutions = TicketResolution.query.filter_by(ticket_id=ticket_id).all()

            # Fetch SLA log data
            logs = TicketEventLog.query.filter_by(ticket_id=ticket_id).all()

            print("Generating CSV data...")

            # Generate CSV data
            csv_data = generate_ticket_csv(ticket_data, ticket_resolutions, logs)
            print(csv_data)
            print("CSV data generated successfully.")

            # Convert CSV data to BytesIO (binary mode)
            byte_data = BytesIO(csv_data.encode('utf-8'))  # encode the string to bytes
            byte_data.seek(0)

            print("byte data ", byte_data)

            # Send CSV as a file download with explicit MIME type
            response = send_file(
                byte_data,
                mimetype="text/csv",
                download_name="ticket_details.csv",
                as_attachment=True
            )

            # Add extra headers to ensure proper content handling
            response.headers["Content-Disposition"] = "attachment; filename=ticket_details.csv"
            response.headers["Content-Type"] = "text/csv; charset=utf-8"

            print("final response ", response)

            return response

        except Exception as e:
            print(f"Error exporting ticket: {str(e)}")
            return jsonify({'error': 'Error exporting ticket'}), 400
