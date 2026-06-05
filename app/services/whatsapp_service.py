import os
from twilio.rest import Client

# =========================================================================
# PRODUCTION ENVIRONMENT VARIABLE CONFIGURATION
# =========================================================================
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")

# Ensure the sender number has the mandatory Twilio gateway 'whatsapp:' prefix
if TWILIO_WHATSAPP_NUMBER and not TWILIO_WHATSAPP_NUMBER.startswith("whatsapp:"):
    TWILIO_WHATSAPP_NUMBER = f"whatsapp:{TWILIO_WHATSAPP_NUMBER}"

# =========================================================================
# AUTOMATED OUTBOUND CLIENT MESSAGING ENGINE
# =========================================================================
def send_whatsapp_message(to_number: str, message: str) -> dict:
    """
    Sanitizes target mobile numbers to enforce country code parameters, lazily instantiates 
    the external REST client API wrapper, and dispatches the outbound transaction body.
    """
    try:
        print("\n=========================")
        print("TWILIO WHATSAPP STARTED")
        print("=========================")

        # 1. CLEAN UP WHITESPACE PADDING
        clean_number = to_number.strip()

        # 2. STRIP OUT DUPLICATE PREFIXES
        if clean_number.startswith("whatsapp:"):
            clean_number = clean_number.replace("whatsapp:", "").strip()

        # 3. COUNTRY CODE CONFIGURATION MATRICES (Enforces India Prefix Logic)
        if not clean_number.startswith("+"):
            if len(clean_number) == 10:
                clean_number = f"+91{clean_number}"
            elif clean_number.startswith("91") and len(clean_number) == 12:
                clean_number = f"+{clean_number}"

        # 4. PACKAGE THE TARGET RECIPIENT URI CORRESPONDENCE
        formatted_to = f"whatsapp:{clean_number}"

        print(f"ACCOUNT SID: {TWILIO_ACCOUNT_SID}")
        print(f"FROM NUMBER: {TWILIO_WHATSAPP_NUMBER}")
        print(f"TO NUMBER: {formatted_to}")
        print(f"MESSAGE: {message}")

        # 5. LAZY OPERATIONAL INITIALIZATION GUARD (Prevents boot startup crashes)
        if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN:
            raise ValueError("Twilio application gateway authentication configuration secrets are missing from context variables.")

        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

        # 6. DISPATCH GATEWAY OPERATION EXECUTION
        response = client.messages.create(
            body=message,
            from_=TWILIO_WHATSAPP_NUMBER,
            to=formatted_to
        )

        print("=========================")
        print("WHATSAPP SENT SUCCESS")
        print("=========================")
        print(f"MESSAGE SID: {response.sid}")

        return {"success": True, "sid": response.sid}

    except Exception as e:
        print("=========================")
        print("TWILIO ERROR")
        print("=========================")
        print(str(e))
        return {"success": False, "error": str(e)}