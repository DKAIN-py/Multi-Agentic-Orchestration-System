# Crewai imports
from crewai.tools import BaseTool

# Email SMTP
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import smtplib

# Monitoring
from agentops.sdk.decorators import tool as ao_tool

# utils
from pydantic import BaseModel, Field
from typing import Type, List
import os



class EmailInput(BaseModel):
    recipient: str = Field(..., description="Email address of the receiver")
    subject: str = Field(..., description="Subject of the email")
    body: str = Field(..., description="Content of the email")
    files: List[str] = Field(...,description="List of file paths to be sent, can be empty if no file to be sent.")

@ao_tool(name="Email Tool")
class SendEmailTool(BaseTool):
    name: str = "Gmail Sender"
    description: str = "Sends an email using Gmail."
    args_schema: Type[BaseModel] = EmailInput

    async def _run(self, recipient: str, subject: str, body: str, files: List[str]) -> str:
        sender_email = os.getenv("COMMUNICATION_EMAIL") 
        sender_password = os.getenv("APP_PASSWORD") 

        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['From'] = sender_email
        msg['To'] = recipient

        msg.attach(MIMEText(body, "plain"))
        
        if files:
            self.sendFile(files, msg)

        try:

            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls() 
                server.login(sender_email, sender_password)
                server.send_message(msg)
            return await f"Email successfully sent to {recipient}"
        except Exception as e:
            return await f"Failed to send email: {str(e)}"
        

    def sendFile(self, files: List[str], msg: MIMEMultipart):

        for file in files:
            if os.path.isfile(file):
                try:
                    with open(file, "rb") as f:
                        part = MIMEBase("application", "octet-stream")
                        part.set_payload(f.read())

                    encoders.encode_base64(part)
                    part.add_header(
                        "Content-Disposition",
                        f"attachment; filename={os.path.basename(file)}"
                    )

                    msg.attach(part)
                
                except Exception as e:
                    print(f"Could not attach: {part}: {e}")