import os
from dotenv import load_dotenv#pour lire env dont il y a les cles secrets twilio
from twilio.rest import Client#l outil de twilio qui nous va permet de comm avec twilio's servers

load_dotenv()#pr lect des api


def send_whatsapp(message_body: str):
    client = Client(
        os.getenv("TWILIO_ACCOUNT_SID"),
        os.getenv("TWILIO_AUTH_TOKEN")
    )

    message = client.messages.create(
        from_=os.getenv("TWILIO_WHATSAPP_FROM"),
        body=message_body[:1550],#car whatsap limite les mssg à 1600==> donc pour eviter bloc
        to=os.getenv("USER_WHATSAPP_TO")
    )

    return message.sid