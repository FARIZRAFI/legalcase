import os

from twilio.rest import Client

from dotenv import load_dotenv



# =========================
# LOAD ENVIRONMENT
# =========================

load_dotenv()



# =========================
# ENV VARIABLES
# =========================

ACCOUNT_SID = os.getenv(
    "TWILIO_ACCOUNT_SID"
)

AUTH_TOKEN = os.getenv(
    "TWILIO_AUTH_TOKEN"
)



# =========================
# WHATSAPP NUMBER
# =========================

TWILIO_WHATSAPP_NUMBER = (
    "whatsapp:+14155238886"
)



# =========================
# VALIDATION
# =========================

if not ACCOUNT_SID:

    raise Exception(
        "TWILIO_ACCOUNT_SID missing"
    )


if not AUTH_TOKEN:

    raise Exception(
        "TWILIO_AUTH_TOKEN missing"
    )



# =========================
# CREATE CLIENT
# =========================

client = Client(

    ACCOUNT_SID,

    AUTH_TOKEN
)



# =========================
# FORMAT NUMBER
# =========================

def format_whatsapp_number(
    number: str
):

    number = number.strip()


    if number.startswith(
        "whatsapp:"
    ):

        return number


    return f"whatsapp:{number}"



# =========================
# SEND WHATSAPP MESSAGE
# =========================

def send_whatsapp_message(

    to_number: str,

    message: str
):

    try:


        # FORMAT NUMBER
        formatted_number = (
            format_whatsapp_number(
                to_number
            )
        )



        # SEND MESSAGE
        response = client.messages.create(

            body=message,

            from_=TWILIO_WHATSAPP_NUMBER,

            to=formatted_number
        )



        print(
            "\n========== WHATSAPP SENT =========="
        )

        print(
            f"SID: {response.sid}"
        )

        print(
            f"TO: {formatted_number}"
        )

        print(
            f"MESSAGE: {message}"
        )

        print(
            "===================================\n"
        )



        return {

            "success":
            True,

            "sid":
            response.sid,

            "to":
            formatted_number,

            "message":
            message
        }



    except Exception as e:


        print(
            "\n========== WHATSAPP ERROR =========="
        )

        print(
            str(e)
        )

        print(
            "====================================\n"
        )



        return {

            "success":
            False,

            "error":
            str(e)
        }