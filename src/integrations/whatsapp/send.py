import os
import httpx
import logging

logger = logging.getLogger('beststag.integrations.whatsapp.send')

async def send_whatsapp_message_via_twilio(to_number: str, message: str) -> dict:
    """Envio simples de mensagem WhatsApp via API Twilio."""
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    from_number = os.getenv("TWILIO_WHATSAPP_FROM")
    if not all([account_sid, auth_token, from_number]):
        raise ValueError("Twilio credentials not configured")

    url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json"
    data = {
        "From": from_number,
        "To": to_number,
        "Body": message,
    }
    async with httpx.AsyncClient(auth=(account_sid, auth_token)) as client:
        resp = await client.post(url, data=data)
        resp.raise_for_status()
        logger.debug(f"Twilio message sent: {resp.json().get('sid')}")
        return resp.json()
