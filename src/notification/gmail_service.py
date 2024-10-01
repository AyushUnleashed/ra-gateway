import aiosmtplib
from email.mime.text import MIMEText
from src.config import Config
from src.utils.constants import Constants

async def send_email(subject, body, sender, recipients, server='smtp.gmail.com', port=465):
    password = Config.GOOGLE_APP_PASSWORD
    """
    Send an email using SMTP with SSL.

    Parameters:
    - subject (str): The subject line of the email.
    - body (str): The body text of the email.
    - sender (str): The sender's email address.
    - recipients (list): A list of email addresses to send the email to.
    - password (str): The password for the sender's email account.
    - server (str): The SMTP server to connect to.
    - port (int): The port number to use for the SMTP server connection.

    Returns:
    - None
    """
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ', '.join(recipients)

    try:
        await aiosmtplib.send(
            message=msg,
            hostname=server,
            port=port,
            username=sender,
            password=password,
            use_tls=True
        )
        print("Email sent!")
    except Exception as e:
        print(f"Failed to send email: {e}")

async def send_video_ready_alert(user_email):
    recipients = [user_email]
    subject = "Your Video Ad is Ready!"
    body = f"""
    <html>
        <body>
            <p>Hello,</p>
            <p>Your video ad has been generated and is now available in your video gallery.</p>
            <p>You can view your ad <a href="https://reelsai.pro/projects">here</a>.</p>
            <br>
            <p>Best regards,</p>
            <p>Ayush - Founder,<br>reelsai.pro</p>
        </body>
    </html>
    """
    await send_email(subject, body, Constants.SENDER_EMAIL, recipients)


if __name__ == "__main__":
    # subject = "Email Subject"
    # body = "This is the body of the text message."
    # sender = "ayushyadavcodes@gmail.com"
    # recipients = ["ayushyadavytube@gmail.com"]
    #
    # send_email(subject, body, sender, recipients)
    send_video_ready_alert("query.superheroai@gmail.com")