import random
import base64
import string
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError, HTTPException
from google.auth.transport.requests import Request
from celery import Celery
from dotenv import load_dotenv
import os

load_dotenv()
RABBITMQ_URL = os.getenv("RABBITMQ_URL")
GMAIL_SENDER_EMAIL = os.getenv("GMAIL_SENDER_EMAIL")
GMAIL_CLIENT_ID = os.getenv("GMAIL_CLIENT_ID")
GMAIL_CLIENT_SECRET = os.getenv("GMAIL_CLIENT_SECRET")
GMAIL_REFRESH_TOKEN = os.getenv("GMAIL_REFRESH_TOKEN")

celery_app = Celery("tasks", broker=RABBITMQ_URL)

def generate_otp(length=6):
    return ''.join(random.choices(string.digits, k=length))

class EmailService:
    def __init__(self):
        self.creds = Credentials(
           token=None,
           refresh_token=GMAIL_REFRESH_TOKEN,
           token_uri="https://oauth2.googleapis.com/token",
           client_id=GMAIL_CLIENT_ID,
           client_secret=GMAIL_CLIENT_SECRET,
           scopes=["https://www.googleapis.com/auth/gmail.send"] 
        )

        self.creds.refresh(Request())
        self.service = build("gmail", "v1", credentials=self.creds)

    def send_welcome_email(self, email : str):
        try:
            message = {'raw' : self._create_welcome_message(email)}
            self.service.users().messages().send(userId="me", body=message).execute()
            print("Welcome email sent successfully!")
        except HttpError as error:
            print(f"Gmail API error: {error}")
            raise HTTPException(status_code=500, detail="Failed to send welcome email due to Gmail API error")
        except Exception as error:
            print(f"An error occurred: {error}")
            raise HTTPException(status_code=500, detail="Failed to send welcome email")
        
    def send_otp_email(self, email : str, otp : str):
        try:
            message = {'raw' : self._create_otp_message(email, otp)}
            self.service.users().messages().send(userId="me", body=message).execute()
            print("OTP email sent successfully!")
        except HttpError as error:
            print(f"Gmail API error: {error}")
            raise HTTPException(status_code=500, detail="Failed to send OTP email due to Gmail API error")
        except Exception as error:
            print(f"An error occurred: {error}")
            raise HTTPException(status_code=500, detail="Failed to send OTP email")


    def _create_welcome_message(self, email : str):
        subject = "Welcome to our Service!"
        message_text = (
            "Hello,\n\n"
            "Thank you for registering with our service! We're excited to have you on board.\n\n"
            "Best regards,\n"
            "The Team"
        )

        email_message = (
            f"From: {GMAIL_SENDER_EMAIL}\r\n"
            f"To: {email}\r\n"
            f"Subject: {subject}\r\n"
            f"\r\n"
            f"{message_text}"
        )

        return base64.urlsafe_b64encode(email_message.encode("utf-8")).decode("utf-8")


    def _create_otp_message(self, email : str):
        subject = "Verify Your Account"
        message_text = (
            "Hello,\n\n"
            "Your OTP is: {otp}. It expires in 10 minutes.\n\n"
            "Best regards,\n"
            "The Team"
        )

        email_message = (
            f"From: {GMAIL_SENDER_EMAIL}\r\n"
            f"To: {email}\r\n"
            f"Subject: {subject}\r\n"
            f"\r\n"
            f"{message_text}"
        )

        return base64.urlsafe_b64encode(email_message.encode("utf-8")).decode("utf-8")
    

email_service = EmailService()

@celery_app.task
def send_welcome_email_task(email : str):
    email_service.send_welcome_email(email)

@celery_app.task
def send_otp_email_task(email : str, otp : str):
    email_service.send_otp_email(email, otp)
