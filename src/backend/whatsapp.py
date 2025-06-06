from datetime import datetime

from fastapi import Form, Response
from twilio.twiml.messaging_response import MessagingResponse

from src.backend.app import app
from src.backend.db import SessionLocal, InboundMessage
from src.backend.ai import respond
from src.backend.memory import context


@app.post("/webhook/twilio")
async def twilio_webhook(
    Body: str = Form(...),
    From: str = Form(...),
    To: str = Form(...),
):
    db = SessionLocal()
    inbound = InboundMessage(
        from_number=From,
        to_number=To,
        message_body=Body,
        timestamp=datetime.utcnow()
    )
    db.add(inbound)
    db.commit()
    db.close()

    context.store_context(user_id=From, message=Body)

    reply_text = respond.generate_response(Body)

    twiml_resp = MessagingResponse()
    twiml_resp.message(reply_text)
    return Response(content=str(twiml_resp), media_type="application/xml")
