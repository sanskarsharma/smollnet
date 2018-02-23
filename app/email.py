from app import app_instance, mail_instance
from flask_mail import Message
from flask import render_template

from threading import Thread


def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    # starting a thread instead of directly calling mail_instance.send() function on our main application thread
    # notice the target of thread is our send_async_email() function which in turn calls mail_instance.send()
    Thread(target= send_async_email, args=(app_instance, msg)).start()

def send_async_email(app_instance, msg):
    with app_instance.app_context():
        mail_instance.send(msg)


def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_email(subject = '[MindBlog] Reset Your Password',
               sender= app_instance.config['ADMINS'][0],
               recipients= [user.email],
               text_body= render_template('email/reset_password_mail.txt', user=user, token=token),
               html_body= render_template('email/reset_password_mail.html', user=user, token=token)
               )

