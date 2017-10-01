from __future__ import absolute_import

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from monitor.models.config import SMTPConfig


class EMail(object):

    def __init__(self, smtp_config):
        """
        Constructor.

        :param smtp_config: the SMTP configuration.
        :type smtp_config: SMTPConfig or dict representing SMTPConfig
        """
        smtp_config.verify()
        self.config = SMTPConfig(smtp_config)

    def send(self, message_body):
        """
        Send message over email.

        :param message_body: the email body
        :return:
        """
        # Prepare actual message
        subject = self.config.subject
        message = message_body

        if type(self.config.subject) == unicode:
            subject = self.config.subject.encode('UTF-8')
        if type(message_body) == unicode:
            message = message_body.encode('UTF-8')

        msg = MIMEMultipart('alternative')
        msg['From'] = self.config.sender
        msg['To'] = self.config.recipient
        msg['Subject'] = subject

        part1 = MIMEText(message, 'plain', "utf-8")
        part2 = MIMEText(message, 'html', "utf-8")
        msg.attach(part1)
        msg.attach(part2)

        server = smtplib.SMTP(self.config.server, self.config.port)
        server.ehlo()
        server.starttls()
        server.login(self.config.user, self.config.password)
        server.sendmail(self.config.user, self.config.recipient, msg.as_string())
        server.close()
