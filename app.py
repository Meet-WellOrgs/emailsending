# from flask import Flask, request, jsonify, session, render_template, url_for, redirect, flash
# from flask_cors import CORS
# import csv
# import threading
# import time
# import io
# import os

# app = Flask(__name__)
# CORS(app)
# app.config['SECRET_KEY'] = 'your_secret_key'

# from mail2 import send_email2

# def send_emails_in_batches(emails, formatted_template, subject, attachments):
#     try:
#         for i in range(0, len(emails), 10):
#             batch = emails[i:i + 10]
#             for email in batch:
#                 send_email2(formatted_template, email.strip(), subject, attachments)  # Strip any extra spaces
#             time.sleep(300)  # Wait 5 minutes before sending the next batch
#     finally:
#         # Remove the attachments after all batches are sent
#         for attachment in attachments:
#             if os.path.exists(attachment):
#                 try:
#                     os.remove(attachment)
#                     print(f"Attachment '{attachment}' has been removed.")
#                 except Exception as e:
#                     print(f"Failed to remove attachment '{attachment}': {e}")



# @app.route('/', methods=['GET', 'POST'])
# def upload_csv():
#     if request.method == 'POST':
#         csv_file = request.files['csv_file']
#         email_subject = request.form['subject']
#         email_template = request.form['email_preview']
#         attachments = request.files.getlist('attachments')

#         if not csv_file:
#             flash('No file uploaded', 'danger')
#             return redirect(request.url)

#         # Process and save attachments to a temporary directory
#         saved_attachments = []
#         for attachment in attachments:
#             if attachment and attachment.content_length <= 10 * 1024 * 1024:  # 10MB size limit
#                 filepath = os.path.join('uploads', attachment.filename)
#                 attachment.save(filepath)
#                 saved_attachments.append(filepath)
#             else:
#                 flash(f"File '{attachment.filename}' exceeds 10MB limit", 'danger')
#                 return redirect(request.url)

#         # Extract emails from CSV, handling BOM in case of UTF-8 encoded files
#         emails = []
#         csv_data = io.StringIO(csv_file.read().decode("utf-8-sig"))  # Using utf-8-sig to handle BOM
#         csv_reader = csv.DictReader(csv_data)

#         for row in csv_reader:
#             if 'mails' in row and row['mails']:
#                 # Split emails by comma and add them to the list
#                 print(row['mails'])
#                 multiple_emails = row['mails'].split(',')
#                 emails.extend(multiple_emails)

#         if not emails:
#             flash('No valid emails found in the CSV', 'danger')
#             return redirect(request.url)

#         # Start a background thread for sending emails
#         threading.Thread(target=send_emails_in_batches, args=(emails, email_template, email_subject, saved_attachments)).start()
        
#         flash('Emails are being sent in batches of 10 every 5 minutes.', 'success')
#         return redirect(url_for('upload_csv'))

#     return render_template('upload_csv.html')


# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=8080)

from flask import Flask, request, jsonify,render_template
from flask_cors import CORS
import csv
import threading
import time
import io
import os

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)
app.config['SECRET_KEY'] = 'your_secret_key'

@app.route('/')
def index():
    return render_template('upload_csv.html')

from mail2 import send_email2

def send_emails_in_batches(emails, formatted_template, subject, attachments):
    try:
        for i in range(0, len(emails), 10):
            batch = emails[i:i + 10]
            for email in batch:
                send_email2(formatted_template, email.strip(), subject, attachments)  # Strip any extra spaces
            time.sleep(300)  # Wait 5 minutes before sending the next batch
    finally:
        # Remove the attachments after all batches are sent
        for attachment in attachments:
            if os.path.exists(attachment):
                try:
                    os.remove(attachment)
                    print(f"Attachment '{attachment}' has been removed.")
                except Exception as e:
                    print(f"Failed to remove attachment '{attachment}': {e}")

# API to handle file upload and email sending (POST request)
@app.route('/upload-csv', methods=['POST'])
def upload_csv():
    csv_file = request.files.get('csv_file')
    email_subject = request.form.get('subject')
    email_template = request.form.get('email_preview')
    attachments = request.files.getlist('attachments')

    # Validate the input
    if not csv_file or not email_subject or not email_template:
        return jsonify({"error": "Missing required fields (csv_file, subject, or email_preview)"}), 400

    # Process and save attachments to a temporary directory
    saved_attachments = []
    for attachment in attachments:
        if attachment and attachment.content_length <= 10 * 1024 * 1024:  # 10MB size limit
            filepath = os.path.join('uploads', attachment.filename)
            attachment.save(filepath)
            saved_attachments.append(filepath)
        else:
            return jsonify({"error": f"File '{attachment.filename}' exceeds 10MB limit"}), 400

    # Extract emails from CSV, handling BOM in case of UTF-8 encoded files
    emails = []
    csv_data = io.StringIO(csv_file.read().decode("utf-8-sig"))  # Using utf-8-sig to handle BOM
    csv_reader = csv.DictReader(csv_data)

    for row in csv_reader:
        if 'mails' in row and row['mails']:
            # Split emails by comma and add them to the list
            multiple_emails = row['mails'].split(',')
            emails.extend(multiple_emails)

    if not emails:
        return jsonify({"error": "No valid emails found in the CSV"}), 400

    # Start a background thread for sending emails
    threading.Thread(target=send_emails_in_batches, args=(emails, email_template, email_subject, saved_attachments)).start()

    return jsonify({"message": "Emails are being sent in batches of 10 every 5 minutes."}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
