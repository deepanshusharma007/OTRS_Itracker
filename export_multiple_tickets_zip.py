from io import StringIO, BytesIO
from flask_cors import cross_origin
from flask_restful import Resource
from flask import request, jsonify, send_file, Response
from models import TicketMaster, SLALog, CustomerMaster
from jwtData import token_required
from datetime import datetime


def generate_multiple_ticket_csv(tickets_data):
    """
    Generates a CSV string for multiple tickets.
    """
    output = StringIO()

    # Write the header row
    output.write(
        "Ticket ID,Customer Name,Title,Description,Breach Status,Raised At,SLA Due,Status,Type,Severity,Bucket\n")

    # Write data for each ticket
    for ticket_data in tickets_data:
        output.write(
            f"{ticket_data['ticket_id']},{ticket_data['customer_name']},{ticket_data['title']},{ticket_data['description']},"
            f"{ticket_data['breach_status']},{ticket_data['raised_at']},{ticket_data['sla_due']},"
            f"{ticket_data['status']},{ticket_data['type']},{ticket_data['severity']},{ticket_data['bucket']}\n"
        )

    return output.getvalue()


class ExportMultipleTickets(Resource):
    @cross_origin()
    @token_required
    def post(self):
        try:
            # Get ticket IDs from the request JSON
            data = request.get_json()
            ticket_ids = data.get('tickets_ids')
            print(ticket_ids)

            if not ticket_ids:
                return jsonify({'error': 'Missing ticket IDs'}), 400

            # Prepare the data for each ticket
            tickets_data = []
            for ticket_id in ticket_ids:
                ticket_data = TicketMaster.query.filter_by(ticket_id=ticket_id).first()
                if not ticket_data:
                    continue

                # Fetch customer name
                customer_name = "N/A"
                if ticket_data.customer_id:
                    customer = CustomerMaster.query.filter_by(customer_id=ticket_data.customer_id).first()
                    if customer:
                        customer_name = customer.customer_name

                # Determine breach status
                breached_status = "N/A"
                latest_sla_log = SLALog.query.filter_by(ticket_id=ticket_id).order_by(SLALog.id.desc()).first()
                sla_due = (
                    latest_sla_log.sla_due.strftime("%Y-%m-%d %H:%M:%S")
                    if latest_sla_log and hasattr(latest_sla_log, 'sla_due')
                    else 'N/A'
                )
                if latest_sla_log:
                    current_time = datetime.now()
                    breached_status = 'breached' if current_time > latest_sla_log.sla_due and ticket_data.status == 'open' else 'not breached'

                # Add ticket details to the list
                tickets_data.append({
                    "ticket_id": ticket_id,
                    "customer_name": customer_name,
                    "title": ticket_data.title,
                    "description": ticket_data.description,
                    "breach_status": breached_status,
                    "raised_at": ticket_data.raised_at,
                    "sla_due": sla_due,
                    "status": ticket_data.status,
                    "type": ticket_data.type if hasattr(ticket_data, 'type') else 'N/A',
                    "severity": ticket_data.severity,
                    "bucket": ticket_data.bucket
                })

            if not tickets_data:
                return jsonify({'error': 'No valid tickets found'}), 404

            print("generating csv data")

            # Generate CSV data
            csv_data = generate_multiple_ticket_csv(tickets_data)
            print(csv_data)
            print("CSV data generated successfully")

            # Convert CSV data to BytesIO (binary mode)
            byte_data = BytesIO(csv_data.encode('utf-8'))
            byte_data.seek(0)

            print("Byte data generated")

            # Create a custom response with explicit binary data
            response = Response(
                byte_data.getvalue(),  # Binary data as body
                mimetype="text/csv",
                headers={
                    "Content-Disposition": "attachment; filename=tickets_summary.csv",
                    "Content-Type": "text/csv; charset=utf-8"
                }
            )

            print("Final response prepared")

            return response

        except Exception as e:
            print(f"Error exporting tickets: {str(e)}")
            return jsonify({'error': 'Error exporting tickets'}), 400
