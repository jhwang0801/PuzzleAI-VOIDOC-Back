from django.core.mail.backends.smtp import BaseEmailBackend
from sqlalchemy import null

class CustomEmailBackend(BaseEmailBackend):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def open(self):
        return null

    def close(self):
        return null

    def send_messages(self, email_messages):
        for message in email_messages:
            recipients = '; '.join(message.to)
            print(f'{recipients} {message.subject}')
        return super().send_messages(email_messages)