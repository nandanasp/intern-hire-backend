from mailersend import emails
from dotenv import load_dotenv
import os
import redis
from rq import Worker, Queue, Connection
from time import sleep 

# Redis connection
load_dotenv()

redis_conn = redis.Redis(host='localhost', port=6379, db=0)
# set `MAILERSEND_API_KEY`` in .env
def send_email(recipient_email: str, status: str):
    mailer = emails.NewEmail(os.getenv('MAILERSEND_API_KEY'))

    def get_email_content(status: str):
        if status == 'ACCEPTANCE':
            subject = "Congratulations on Your Application!"
            html_content = (
                "<p>Dear Applicant,</p>"
                "<p>Congratulations! We are pleased to inform you that your application has been successful.</p>"
                "<p>We look forward to having you join our team. Further details about your onboarding will be shared with you shortly.</p>"
                "<p>Thank you for your interest in our company.</p>"
                "<p>Best regards,</p>"
                "<p>Your Company Name</p>"
            )
            plaintext_content = (
                "Dear Applicant,\n\n"
                "Congratulations! We are pleased to inform you that your application has been successful.\n\n"
                "We look forward to having you join our team. Further details about your onboarding will be shared with you shortly.\n\n"
                "Thank you for your interest in our company.\n\n"
                "Best regards,\n"
                "Your Company Name"
            )
        elif status == 'REJECTION':
            subject = "Application Status Update"
            html_content = (
                "<p>Dear Applicant,</p>"
                "<p>Thank you for applying to our company. We appreciate the time and effort you put into your application.</p>"
                "<p>After careful consideration, we regret to inform you that we will not be moving forward with your application at this time.</p>"
                "<p>We encourage you to apply for future openings that match your skills and experience.</p>"
                "<p>Thank you again for your interest in our company.</p>"
                "<p>Best regards,</p>"
                "<p>Your Company Name</p>"
            )
            plaintext_content = (
                "Dear Applicant,\n\n"
                "Thank you for applying to our company. We appreciate the time and effort you put into your application.\n\n"
                "After careful consideration, we regret to inform you that we will not be moving forward with your application at this time.\n\n"
                "We encourage you to apply for future openings that match your skills and experience.\n\n"
                "Thank you again for your interest in our company.\n\n"
                "Best regards,\n"
                "Your Company Name"
            )

        return subject, html_content, plaintext_content

    subject, html_content, plaintext_content = get_email_content(status)

    mail_body = {}
    mail_from = {
        "name": "Sumrender Singh",
        "email": "sumrender.s@trial-jy7zpl9z6n045vx6.mlsender.net",
    }
    recipients = [
        {
            "name": "Sumrender Singh",
            "email": recipient_email,
        }
    ]

    reply_to = {
        "name": "HR Department",
        "email": "hr@trial-jy7zpl9z6n045vx6.mlsender.net",
    }

    mailer.set_mail_from(mail_from, mail_body)
    mailer.set_mail_to(recipients, mail_body)
    mailer.set_subject(subject, mail_body)
    mailer.set_html_content(html_content, mail_body)
    mailer.set_plaintext_content(plaintext_content, mail_body)
    mailer.set_reply_to(reply_to, mail_body)

    res = mailer.send(mail_body)
    return res


def send_email_bulk(mail_list):
    for mail in mail_list:
        send_email(mail['recipient_email'], mail['status'])

        sleep(2)
        

        
# if __name__ == "__main__":
#     recipient_email = "devendra.r@fyle.in"
#     is_acceptance = False

#     result = send_email(recipient_email, is_acceptance)
#     print(result)

if __name__ == '__main__':
    with Connection(redis_conn):
        worker = Worker(['llms', 'default'])
        worker.work()