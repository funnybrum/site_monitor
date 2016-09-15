# -*- encoding: utf-8 -*-
from __future__ import absolute_import

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

SMTP_CONFIG = {
    'server': 'smtp.gmail.com',
    'port': 587,
    'sender': u'Монитор за обяви',
}


def send_email(subject, message, recipient, smtp_config):
    # Prepare actual message
    if type(subject) == unicode:
        subject = subject.encode('UTF-8')
    if type(message) == unicode:
        message = message.encode('UTF-8')

    SMTP_CONFIG.update({'recipient': recipient})

    msg = MIMEMultipart('alternative')
    msg['From'] = SMTP_CONFIG['sender']
    msg['To'] = SMTP_CONFIG['recipient']
    msg['Subject'] = subject

    part1 = MIMEText(message, 'plain', "utf-8")
    part2 = MIMEText(message, 'html', "utf-8")
    msg.attach(part1)
    msg.attach(part2)

    server = smtplib.SMTP(SMTP_CONFIG['server'], SMTP_CONFIG['port'])
    server.ehlo()
    server.starttls()
    server.login(smtp_config['user'], smtp_config['password'])
    server.sendmail(smtp_config['user'], SMTP_CONFIG['recipient'], msg.as_string())
    server.close()
