import streamlit as st
import pandas as pd
import threading
import time
import os
from mail2 import send_email2

# Function to send emails in batches
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

# Streamlit interface
st.title("Email Sender")

# File upload for CSV
csv_file = st.file_uploader("Upload CSV (must contain 'mails' column):", type=['csv'])

# Subject input
email_subject = st.text_input("Email Subject")

# Email template input
email_template = st.text_area("Email Template", "Hello,\n\nThis is a preview of your email. You can customize this template to match your needs.")

# File upload for attachments
attachments = st.file_uploader("Upload Attachments (up to 10MB each):", type=None, accept_multiple_files=True)

# Button to start email sending process
if st.button("Start Sending Emails"):
    if not csv_file or not email_subject or not email_template:
        st.error("Please provide all the required inputs.")
    else:
        # Save attachments to a temporary directory
        saved_attachments = []
        if attachments:
            os.makedirs("uploads", exist_ok=True)
            for attachment in attachments:
                if attachment.size <= 10 * 1024 * 1024:  # 10MB size limit
                    filepath = os.path.join("uploads", attachment.name)
                    with open(filepath, "wb") as f:
                        f.write(attachment.read())
                    saved_attachments.append(filepath)
                else:
                    st.error(f"File '{attachment.name}' exceeds 10MB limit")
                    st.stop()

        # Process the uploaded CSV to extract emails
        try:
            df = pd.read_csv(csv_file)
            if 'mails' in df.columns:
                emails = []
                for email in df['mails']:
                    # Split multiple emails in one field by comma
                    emails.extend(email.split(','))
                emails = [email.strip() for email in emails if email.strip()]  # Clean whitespace
            else:
                st.error("CSV must contain a 'mails' column.")
                st.stop()
        except Exception as e:
            st.error(f"Error processing CSV: {e}")
            st.stop()

        if not emails:
            st.error("No valid emails found in the CSV.")
        else:
            # Start the background email-sending thread
            threading.Thread(target=send_emails_in_batches, args=(emails, email_template, email_subject, saved_attachments)).start()
            st.success("Emails are being sent in batches of 10 every 5 minutes.")
