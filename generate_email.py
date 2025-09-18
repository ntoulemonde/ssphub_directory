import email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def generate_eml_file(email_body, recipient, subject, sender_email =":DG75-SSPHUB-Contact <SSPHUB-contact@insee.fr>"):
    # Create a multipart message
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['BCC'] = recipient
    msg['To'] = sender_email   # Auto send the email
    msg['From'] = 'SELECT THE RIGHT EMAIL'  # Set the sender's email address
    msg['X-Unsent'] = '1'  # Mark the email as unsent : when he file is opened, it can be sent. 

    # Attach the HTML body
    msg.attach(MIMEText(email_body, 'html'))

    # Save the email as an .eml file
    eml_file_path = 'email.eml'
    with open(eml_file_path, 'wb') as f:
        f.write(msg.as_bytes())

    print(f"Email saved as {eml_file_path}")

# Example usage
# email_body = "<html><body><h1>Hello, World!</h1></body></html>"
# recipient = "<goufrunoitridoi-3309@yopmail.com>; <crelonnoyevoi-1576@yopmail.com>"
# subject = "Test Email"

# generate_eml_file(email_body, recipient, subject)

# Example usage
if __name__ == "__main__":
    body = "<h1>Hello, World!</h1><p>This is a test email.</p>"
    recipients = "<recipient1@example.com>; <recipient2@example.com>"
    subject = "Test Email"
    generate_email(body, recipients, subject)

