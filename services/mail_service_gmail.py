from threading import Thread
from flask_mail import Message

from flask_mail import Mail, Message

from app import app
from app import mail
from resources.errors import InternalServerError

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = '****@gmail.com'
app.config['MAIL_PASSWORD'] = 'password'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)


def send_async_email(app, msg):
    with app.app_context():
        try:
            mail.send(msg)
        except ConnectionRefusedError:
            raise InternalServerError("[MAIL SERVER] not working")


def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email, args=(app, msg)).start()
