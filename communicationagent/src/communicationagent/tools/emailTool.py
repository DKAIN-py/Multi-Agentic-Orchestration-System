import smtplib
from email.mime.text import MIMEText
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type
import os

# 1. Define the Input Schema
class EmailInput(BaseModel):
    recipient: str = Field(..., description="Email address of the receiver")
    subject: str = Field(..., description="Subject of the email")
    body: str = Field(..., description="Content of the email")

# 2. Create the Tool
class SendEmailTool(BaseTool):
    name: str = "Gmail Sender"
    description: str = "Sends an email using Gmail."
    args_schema: Type[BaseModel] = EmailInput

    def _run(self, recipient: str, subject: str, body: str) -> str:
        sender_email = os.getenv("COMMUNICATION_EMAIL") # Load from .env
        sender_password = os.getenv("APP_PASSWORD") # Load from .env

        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = sender_email
        msg['To'] = recipient

        try:
            # Connect to Gmail Server
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls() # Secure the connection
                server.login(sender_email, sender_password)
                server.send_message(msg)
            return f"Email successfully sent to {recipient}"
        except Exception as e:
            return f"Failed to send email: {str(e)}"