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

        # 1. Clean up spaces or brackets
        clean_number = to_number.strip()

        # 2. Strip out 'whatsapp:' if it was accidentally passed twice
        if clean_number.startswith("whatsapp:"):
            clean_number = clean_number.replace("whatsapp:", "").strip()

        # 3. CRITICAL: Automatically inject the +91 country prefix if missing
        if not clean_number.startswith("+"):
            # If it's a standard 10-digit Indian number, snap +91 to the front
            if len(clean_number) == 10:
                clean_number = f"+91{clean_number}"
            else:
                # Fallback safeguard for numbers that might already have '91' but no '+'
                if clean_number.startswith("91") and len(clean_number) == 12:
                    clean_number = f"+{clean_number}"

        # 4. Final Twilio string packaging
        formatted_to = f"whatsapp:{clean_number}"

        print("ACCOUNT SID:", TWILIO_ACCOUNT_SID)
        print("FROM NUMBER:", TWILIO_WHATSAPP_NUMBER)
        print("TO NUMBER:", formatted_to)
        print("MESSAGE:", message)

        # SEND MESSAGE VIA CLIENT
        response = client.messages.create(
            body=message,
            from_=TWILIO_WHATSAPP_NUMBER,
            to=formatted_to
        )

        print("=========================")
        print("WHATSAPP SENT SUCCESS")
        print("=========================")
        print("MESSAGE SID:", response.sid)

        return {"success": True, "sid": response.sid}

    except Exception as e:
        print("=========================")
        print("TWILIO ERROR")
        print("=========================")
        print(str(e))
        return {"success": False, "error": str(e)}