import os
from dotenv import load_dotenv
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

load_dotenv()

def send_email2(template, attendees, subject, attachments=None):
    from_email = "support@employo.co.in"
    from_password = "sFttJcRQE9dr"
    
    # Set up the MIME
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = attendees
    msg['Subject'] = subject
    msg.attach(MIMEText(template, 'plain'))

    # Attach files if provided
    if attachments:
        for attachment in attachments:
            filename = os.path.basename(attachment)
            with open(attachment, "rb") as f:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f'attachment; filename= {filename}')
                msg.attach(part)

    # Send the email
    try:
        server = smtplib.SMTP_SSL('smtppro.zoho.in', 465)
        server.login(from_email, from_password)
        text = msg.as_string()
        server.sendmail(from_email, attendees, text)
        server.quit()
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False
