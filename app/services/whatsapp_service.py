import os

from twilio.rest import Client

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")

TWILIO_WHATSAPP_NUMBER = os.getenv(
    "TWILIO_WHATSAPP_NUMBER"
)

client = Client(
    TWILIO_ACCOUNT_SID,
    TWILIO_AUTH_TOKEN
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

        return {
            "success": True,
            "sid": response.sid
        }

    except Exception as e:

        return {
            "success": False,
            "error": str(e)
        }