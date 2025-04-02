from celery import Celery
from dotenv import load_dotenv
import os

load_dotenv()

RABBITMQ_URL = os.getenv("RABBITMQ_URL")

celery_app = Celery("worker", broker=RABBITMQ_URL)
celery_app.conf.task_routes = {
    "app.utils.tasks.send_otp_email_task": {"queue": "email"},
    "app.utils.tasks.send_welcome_email_task": {"queue": "email"},
    "app.utils.tasks.send_reset_password_otp_email_task": {"queue": "email"}
}