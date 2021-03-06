from app import app_instance, mail_instance, celery
from flask_mail import Message
from flask import render_template

from threading import Thread


# def send_email(subject, sender, recipients, text_body, html_body):
    
#     send_async_email_task.delay(subject=subject,sender=sender,recipients=recipients,text_body=text_body,html_body=html_body)
    

    # starting a thread instead of directly calling mail_instance.send() function on our main application thread
    # notice the target of thread is our send_async_email() function which in turn calls mail_instance.send()
    # Thread(target= send_async_email, args=(app_instance, msg)).start()


@celery.task
def send_async_email_task(subject, sender, recipients, text_body, html_body):
    #print("hello")
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body

    with app_instance.app_context():
        mail_instance.send(msg)


def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_async_email_task.delay(subject = '[smollnet] Reset Your Password',
               sender= app_instance.config['ADMINS'][0],
               recipients= [user.email],
               text_body= render_template('email/reset_password_mail.txt', user=user, token=token),
               html_body= render_template('email/reset_password_mail.html', user=user, token=token)
               )

