import os
from twilio.rest import Client

# =========================
# ENV VARIABLES
# =========================
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")

# Ensure the sender number has the mandatory 'whatsapp:' prefix
if TWILIO_WHATSAPP_NUMBER and not TWILIO_WHATSAPP_NUMBER.startswith("whatsapp:"):
    TWILIO_WHATSAPP_NUMBER = f"whatsapp:{TWILIO_WHATSAPP_NUMBER}"

# =========================
# TWILIO CLIENT
# =========================
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# =========================
# SEND WHATSAPP MESSAGE
# =========================
def send_whatsapp_message(to_number: str, message: str):
    try:
        print("\n=========================")
        print("TWILIO WHATSAPP STARTED")
        print("=========================")

        # Clean the recipient number format dynamically
        formatted_to = to_number.strip()
        if not formatted_to.startswith("whatsapp:"):
            formatted_to = f"whatsapp:{formatted_to}"

        print("ACCOUNT SID:", TWILIO_ACCOUNT_SID)
        print("FROM NUMBER:", TWILIO_WHATSAPP_NUMBER)
        print("TO NUMBER:", formatted_to)
        print("MESSAGE:", message)

        # SEND MESSAGE
        response = client.messages.create(
            body=message,
            from_=TWILIO_WHATSAPP_NUMBER,
            to=formatted_to
        )

        print("=========================")
        print("WHATSAPP SENT SUCCESS")
        print("=========================")
        print("MESSAGE SID:", response.sid)

        return {
            "success": True,
            "sid": response.sid
        }

    except Exception as e:
        print("=========================")
        print("TWILIO ERROR")
        print("=========================")
        print(str(e))

        return {
            "success": False,
            "error": str(e)
        }