from twilio.rest import Client
from dotenv import load_dotenv
import os

load_dotenv()

ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")

TWILIO_WHATSAPP_NUMBER = "whatsapp:+14155238886"

client = Client(
    ACCOUNT_SID,
    AUTH_TOKEN
)


def send_whatsapp_message(
    to_number: str,
    message: str
):
    try:
        response = client.messages.create(
            body=message,
            from_=TWILIO_WHATSAPP_NUMBER,
            to=f"whatsapp:{to_number}"
        )

        print("\n========== WHATSAPP SENT ==========")
        print(f"SID: {response.sid}")
        print(f"TO: {to_number}")
        print(message)
        print("===================================\n")

    except Exception as e:
        print("\n========== WHATSAPP ERROR ==========")
        print(str(e))
        print("====================================\n")