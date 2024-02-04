from collections.abc import Iterable
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import formatdate
from email.message import Message
from email import encoders
from typing import Any
import logging
import sys
import os

from daily_email_report.data_validation import validate_email, validate_filepaths


logger = logging.getLogger(__name__)


def write_email(
        sender: str,
        recipients: Iterable[str],
        subject: str,
        email_content: str,
        attachments: Iterable[os.PathLike]
) -> Message:
    """Create an email message.

    :param sender: The email address the email should be addressed from.
    :param recipients: The email addresses the email should be sent to.
    :param subject: The subject of the email.
    :param email_content: The text body of the email.
    :param attachments: Paths to any files to be attached to the email.
    :return: The drafted email.
    """
    message = MIMEMultipart()
    message["From"] = sender
    message["To"] = ", ".join(recipients)
    message["Date"] = formatdate(localtime=True)
    message["Subject"] = subject

    message.attach(MIMEText(email_content, "plain"))
    for file_path in attachments:
        with open(file_path, "rb") as file:
            attachment = MIMEBase('application', 'octet-stream')
            attachment.set_payload(file.read())
            encoders.encode_base64(attachment)
            attachment.add_header("Content-Disposition",
                                  f"attachment; filename= {file_path}")
            message.attach(attachment)

    return message


def draft_email(email_config: dict[str, Any]):
    """Write an ``email.message.Message`` object with given configuration.

    :param email_config: The email configuration from ``config.toml``.
    :return: A Message object.
    """
    try:
        sender = validate_email(email_config["sender"])
    except ValueError as error:
        logger.error(str(error))
        sys.exit(str(error))

    subject: str = email_config["subject"]

    with open(email_config["email_content"]) as email_content_file:
        email_body = email_content_file.read()

    try:
        attachments = validate_filepaths(email_config["attachments"])
    except FileNotFoundError as error:
        logger.error(str(error))
        sys.exit(str(error))

    logger.info("Emails being sent as %s", sender)

    return write_email(
        sender, (), subject, email_body, attachments
    )
