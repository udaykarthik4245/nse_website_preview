import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os

def send_email_report(recipient, start_time, end_time, time_taken, files_attempted, successful_downloads, failed_downloads, log_file_path):
    sender_email = "udaykarthik58@gmail.com"
    sender_password = "glvf mqed wyny msf"  # Replace with the actual password or use environment variables for security
    
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient
    msg['Subject'] = "NSE Report Download Summary"

    body = f"""
    Dear User,

    The automated download of NSE reports has been completed. Below is a summary of the operation:

    Start Time: {start_time}
    End Time: {end_time}
    Total Duration: {time_taken}

    Files Attempted: {files_attempted}
    Successfully Downloaded: {successful_downloads}
    Failed Downloads: {failed_downloads}

    Please find the attached log file for detailed information.

    Best regards,
    Automated System
    """
    msg.attach(MIMEText(body, 'plain'))

    if os.path.exists(log_file_path):
        with open(log_file_path, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition",
            f"attachment; filename= {os.path.basename(log_file_path)}",
        )
        msg.attach(part)

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient, msg.as_string())
        print("Email sent successfully.")
    except Exception as e:
        print(f"Failed to send email: {e}")