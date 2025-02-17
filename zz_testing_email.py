import os
import random
import smtplib
from datetime import datetime
from threading import Thread
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()


def generate_otp():
    fixed_digits = 6
    return random.randrange(111111, 999999, fixed_digits)


def send_otp_async(recipient, otp, sender_email, sender_password):
    """
    Sends an email with the generated OTP to the recipient asynchronously using a thread.

    Args:
        recipient (str): Email address of the recipient.
        otp (str): The generated OTP.
        sender_email (str): Email address of the sender.
        sender_password (str): Password for the sender's email account.
    """

    def send_otp():
        """
        Sends the email using SMTP connection within the thread.
        """

        subject = "Your OTP is: " + str(otp)
        html_message = f"""
        <!DOCTYPE html>
        <html>
        <head>
        <title>----OTP----</title>
        </head>
        <body>
        <h2>Your OTP</h2>

        <p>Dear {recipient},</p>

        <ul>
            <li><strong>OTP:</strong> {otp}</li>
        </ul>

        <p>Best regards,</p>
        <p>OTRS Support Team</p>
        </body>
        </html>
        """

        msg = MIMEText(html_message, 'html')
        msg['Subject'] = subject
        msg['From'] = sender_email
        msg['To'] = recipient

        try:
            server = smtplib.SMTP(os.getenv('SMTP_SERVER'), os.getenv('SMTP_PORT'))
            server.connect(os.getenv('SMTP_SERVER'), os.getenv('SMTP_PORT'))
            server.starttls()  # Attempt to establish TLS connection for security (optional)
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, [recipient], msg.as_string())
            print(f"OTP sent successfully to {recipient}")
        except smtplib.SMTPException as e:
            print(f"Error sending OTP via SMTP: {e}")
        finally:
            if server is not None:
                server.quit()

    # Create and start the thread
    email_thread = Thread(target=send_otp)
    email_thread.start()


if __name__ == "__main__":
    recipient = "deepanshu2210sharma@gmail.com"  # Replace with actual recipient email
    sender_email = "SOCL1@proteantech.in"    # Replace with actual sender email
    sender_password = "!@poiu34"           # Replace with actual sender password (consider more secure approaches)

    otp = generate_otp()
    send_otp_async(recipient, otp, sender_email, sender_password)

    # Continue with other program logic here, avoiding blocking operations
    print("Main program continues to execute...")