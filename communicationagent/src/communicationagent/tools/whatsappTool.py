from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type
from twilio.rest import Client
import os

class WhatsAppInput(BaseModel):
    phone: str = Field(..., description="Phone number to send to (must include country code, e.g., +1555...)")
    message: str = Field(..., description="The text message to send")

class SendWhatsAppTool(BaseTool):
    name: str = "WhatsApp Sender"
    description: str = "Sends a WhatsApp message via Twilio."
    args_schema: Type[BaseModel] = WhatsAppInput

    def _run(self, phone: str, message: str) -> str:
        account_sid = os.getenv("TWILIO_SID")
        auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        from_number = "whatsapp:+14155238886" 

        try:
            client = Client(account_sid, auth_token)
            
            
            if not phone.startswith("whatsapp:"):
                phone = f"whatsapp:{phone}"

            message = client.messages.create(
                body=message,
                from_=from_number,
                to=phone
            )
            return f"WhatsApp message sent! ID: {message.sid}"
        except Exception as e:
            return f"Error sending WhatsApp: {str(e)}"