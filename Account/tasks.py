from twilio.rest import Client

from VeneziaStone.settings import  SENDSMS_FROM_NUMBER, SENDSMS_ACCOUNT_SID, SENDSMS_AUTH_TOKEN
from VeneziaStone.celery import app
from .models import *

"""
Запуск брокера : "redis-server"
Запуск воркеров CELERY : "celery -A VeneziaStone worker --loglevel=info --pool=solo"
Запуск логгера FLOWER: "flower -A VeneziaStone"
"""

@app.task
def sms_send(code_id, body):
    code = Code.objects.get(id=code_id)
    user = code.user
    phone = str(user.phone)
    try:
        client = Client(SENDSMS_ACCOUNT_SID,SENDSMS_AUTH_TOKEN)
        client.messages.create(
            to=phone,
            from_=SENDSMS_FROM_NUMBER,
            body=body
        )
        return {'sended':'True'}
    except Exception:
        return {'sended':'False'}

@app.task
def delete_sms(id):
    try:
        Code.objects.get(id = id).delete()
        return {'deleted':'True'}
    except Exception:
        return {'error':'False'}
