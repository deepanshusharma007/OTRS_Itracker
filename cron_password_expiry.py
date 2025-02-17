import os
import secrets
import smtplib
from email.mime.text import MIMEText
from threading import Thread
from dotenv import load_dotenv

import mysql.connector
from flask import url_for
from mysql.connector import Error
from datetime import datetime, timedelta

from flask import Flask

from app import app

app.config['SERVER_NAME'] = '127.0.0.1:5000'

db_config = {
    'host': 'localhost',
    # 'user': 'dbuserA308',
    'user': 'root',
    # 'password': 'Nsdl@12345%',
    'password': 'root',
    'database': 'OTRS_ticketing_db'
}


def password_expired_async(recipients, sender_email, token, days_left):
    """
    Sends an email with the generated reset link asynchronously using a thread.

    Args:
        recipients (list): List of email addresses of the recipients.
        sender_email (str): Email address of the sender.
        token (str): Password reset token.
    """

    sender_password = os.getenv('SMTP_PASSWORD')

    def password_expired():
        with app.app_context():
            print("entered in password expiry email function.....")
            subject = "Password Expired!!"
            html_message = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>----OTP----</title>
            </head>
            <body>
                <p>Hi,</p>
                
                <p>Your password will expire in {days_left} days. Please reset it soon.</p>

                <p>Click the following link to reset your password: {url_for('reset_password', token=token, _external=True)}</p>

                <br>
                <p>Best regards,</p>
                <p>OTRS Support Team</p>
            </body>
            </html>
            """

            msg = MIMEText(html_message, 'html')
            msg['Subject'] = subject
            msg['From'] = sender_email
            msg['To'] = recipients
            print("Entering into try block.....")
            try:
                print("Entered into try.....")
                server = smtplib.SMTP(os.getenv('SMTP_SERVER'), os.getenv('SMTP_PORT'))
                server.connect(os.getenv('SMTP_SERVER'), os.getenv('SMTP_PORT'))
                server.starttls()  # Attempt to establish TLS connection for security (optional)
                server.login(sender_email, sender_password)
                server.sendmail(sender_email, recipients, msg.as_string())
                print(f"Password expiry email sent successfully to {recipients}")
            except smtplib.SMTPException as e:
                print(f"Error sending Password expiry email: {e}")
            finally:
                if server is not None:
                    server.quit()

    # Create and start the thread
    email_thread = Thread(target=password_expired)
    email_thread.start()


# def password_expiry():
#     try:
#         connection = mysql.connector.connect(**db_config)
#         if connection.is_connected():
#             cursor = connection.cursor()
#             now = datetime.now()
#
#             # update_query = """
#             # UPDATE User
#             # SET password = "-1"
#             # WHERE created_at < NOW() - INTERVAL 45 DAY;
#             # """
#             # cursor.execute(update_query)
#
#             select_query = """
#                         SELECT * from User
#                         WHERE created_at < NOW() - INTERVAL 45 DAY
#                         AND created_at >= NOW() - INTERVAL 60 DAY;
#                         """
#             cursor.execute(select_query)
#
#             results = cursor.fetchall()
#             user_emails = [result[3] for result in results]  # Access the 3rd element (index 2)
#
#             print(user_emails)
#
#             for user in results:
#                 # Check if a token already exists
#                 user_id = user[0]
#                 existing_token_query = """
#                 SELECT * from password_expiry
#                 where user_id=%s
#                 """
#                 cursor.execute(existing_token_query, (user_id,))
#                 existing_token = cursor.fetchall()
#                 print("password expiry query executed")
#
#                 if not existing_token:
#                     # Generate a unique token
#                     token = secrets.token_urlsafe(16)
#                     expiry_date = datetime.now() + timedelta(days=15)
#                     insert_token_query = """
#                                         INSERT INTO password_expiry (user_id, token, expiry_date)
#                                         VALUES (%s, %s, %s)
#                                         """
#                     cursor.execute(insert_token_query, (user_id, token, expiry_date))
#                     sender_email = "SOCL1@proteantech.in"
#                     password_expired_async(user_emails, sender_email, token)
#                 else:
#                     sender_email = "SOCL1@proteantech.in"
#                     for token in existing_token:
#                         print(token[1])
#                         password_expired_async(user_emails, sender_email, token[1])
#
#             connection.commit()
#
#     except Error as e:
#         print(f"Error: ", e)
#
#
# password_expiry()


def password_expiry():
    try:
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            cursor = connection.cursor()
            now = datetime.now()

            # Fetch users who have been registered for between 45 and 60 days
            select_query = """
                        SELECT * from User
                        WHERE updated_at < NOW() - INTERVAL 45 DAY
                        AND updated_at >= NOW() - INTERVAL 60 DAY;
                        """
            cursor.execute(select_query)

            results = cursor.fetchall()
            user_emails = [result[3] for result in results]  # Access the 3rd element (email)

            print(user_emails)

            for user in results:
                user_id = user[0]
                updated_at = user[9]  # Assuming 'created_at' is at index 8, adjust if needed

                existing_token_query = """
                SELECT * from password_expiry
                where user_id=%s
                """
                cursor.execute(existing_token_query, (user_id,))
                existing_token = cursor.fetchall()

                print("password expiry query executed ", user[3])

                # Calculate expiry date (updated_at + 60 days)
                expiry_date = updated_at + timedelta(days=60)

                if not existing_token:
                    # Generate a unique token and insert it into the database
                    token = secrets.token_urlsafe(16)
                    insert_token_query = """
                                        INSERT INTO password_expiry (user_id, token, expiry_date)
                                        VALUES (%s, %s, %s)
                                        """
                    cursor.execute(insert_token_query, (user_id, token, expiry_date))

                    # Calculate how many days are left until expiration and send emails dynamically
                    days_left = (expiry_date - now).days
                    print("days left", days_left)
                    if 1 <= days_left <= 15:  # Send emails for days 1 to 15
                        password_expired_async(user[3], "SOCL1@proteantech.in", token, days_left)
                else:
                    for token_entry in existing_token:
                        token = token_entry[1]
                        print(token)
                        expiry_date = token_entry[2]
                        print(expiry_date)
                        # Calculate how many days are left until expiration
                        days_left = (expiry_date - now).days
                        print("days left already token present", days_left)
                        if 1 <= days_left <= 15:  # Send emails for days 1 to 15
                            password_expired_async(user[3], "SOCL1@proteantech.in", token, days_left)

            connection.commit()

    except Error as e:
        print(f"Error: ", e)


password_expiry()

