import smtplib
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr
from src.config import Config
from src.utils.constants import Constants
from src.utils.logger import logger

async def send_email(subject, body, sender, sender_title, recipients, server='smtp.zoho.in', port=465):
    password = Config.ZOHO_APP_PASSWORD
    """
    Send an email using SMTP with SSL.

    Parameters:
    - subject (str): The subject line of the email.
    - body (str): The body text of the email.
    - sender (str): The sender's email address.
    - sender_title (str): The sender's name or title.
    - recipients (list): A list of email addresses to send the email to.
    - server (str): The SMTP server to connect to.
    - port (int): The port number to use for the SMTP server connection.

    Returns:
    - None
    """
    msg = MIMEText(body, 'html', 'utf-8')
    msg['Subject'] = Header(subject, 'utf-8')
    msg['From'] = formataddr((str(Header(sender_title, 'utf-8')), sender))
    msg['To'] = ', '.join(recipients)

    try:
        logger.info("Connecting to SMTP server...")
        server = smtplib.SMTP_SSL(host=server, port=port)
        server.login(sender, password)
        server.send_message(msg)
        logger.info(f"Email sent successfully to: {recipients}")
    except Exception as e:
        logger.error(f"Failed to send email: {e}")

async def send_video_ready_alert(user_email:str, project_id:str):
    try:
        recipients = [user_email]
        subject = "Your Video Ad is Ready!"
        body = f"""
        <html>
            <body>
                <p>Hello,</p>
                <p>Your video ad has been generated and is now available in your projects section.</p>
                <p>You can view your ad <a href="https://www.reelsai.pro/projects/{project_id}">here</a>.</p>
                <br>
                <p>Best regards,</p>
                <p>Ayush - Founder,<br>reelsai.pro</p>
            </body>
        </html>
        """
        sender_title = "Ayush - ReelsAI"
        await send_email(subject, body, Constants.SENDER_EMAIL, sender_title, recipients)
    except Exception as e:
        logger.error(f"Failed to send video ready alert email: {e}")

if __name__ == "__main__":
    # For testing purposes
    import asyncio
    asyncio.run(send_video_ready_alert("ayushyadavcodes@gmail.com","46b8cc8a-70bd-4b60-8fc2-9e8bdbffdd4a"))