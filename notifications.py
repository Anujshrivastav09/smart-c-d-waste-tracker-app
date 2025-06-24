import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ✅ Email Notification Function
def send_email(to_email, subject, content):
    from_email = "anujshrivastav9540@gmail.com"         
    password = "vllksvkldfkntccg"          

    msg = MIMEMultipart()
    msg["From"] = from_email
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(content, 'plain'))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(from_email, password)
            server.send_message(msg)
        print("✅ Email sent successfully!")
    except smtplib.SMTPAuthenticationError:
        print("❌ Authentication failed. Use App Password, not Gmail password.")
    except Exception as e:
        print(f"❌ Email failed: {e}")

# ✅ SMS Notification Function (Dummy or Real via Twilio)
def send_sms(to_number, body_text):
    try:
        # Uncomment and fill with Twilio credentials to activate
        # from twilio.rest import Client
        # client = Client("TWILIO_SID", "TWILIO_AUTH_TOKEN")
        # message = client.messages.create(
        #     body=body_text,
        #     from_="+1XXXXXXXXXX",  # Replace with your Twilio number
        #     to=to_number
        # )
        # print("✅ SMS sent:", message.sid)

        # Dummy print for testing
        print(f"📱 SMS to {to_number}: {body_text}")
    except Exception as e:
        print(f"❌ SMS failed: {e}")
