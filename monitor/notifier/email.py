# -*- encoding: utf-8 -*-
from __future__ import absolute_import

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class EMail(object):

    @classmethod
    def send(cls, smtp_config, message_body):
        """
        Send message over email.

        :param smtp_config: the smtp config. Specifies stuff like user name, password, port, server, recipient, sender
        and subject
        :param message_body: the email body
        :return:
        """
        # Prepare actual message
        subject = smtp_config.subject
        message = message_body

        if type(smtp_config.subject) == unicode:
            subject = smtp_config.subject.encode('UTF-8')
        if type(message_body) == unicode:
            message = message_body.encode('UTF-8')

        msg = MIMEMultipart('alternative')
        msg['From'] = smtp_config.sender
        msg['To'] = smtp_config.recipient
        msg['Subject'] = subject

        part1 = MIMEText(message, 'plain', "utf-8")
        part2 = MIMEText(message, 'html', "utf-8")
        msg.attach(part1)
        msg.attach(part2)

        server = smtplib.SMTP(smtp_config.server, smtp_config.port)
        server.ehlo()
        server.starttls()
        server.login(smtp_config.user, smtp_config.password)
        server.sendmail(smtp_config.user, smtp_config.recipient, msg.as_string())
        server.close()
