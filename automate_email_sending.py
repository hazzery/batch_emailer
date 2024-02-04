from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import formatdate
from email.message import Message
from email import encoders
from typing import Iterable, Any
import tomllib
import smtplib
import pathlib
import logging
import socket
import sched
import sys
import re
import os

from logging_config import configure_logging

logger = logging.getLogger("automate_email_sending")


def validate_email(email_string: str) -> str:
    """Verify that ``email_string`` is a valid email_address.

    :param email_string: The string email address.
    :return: The string email address.
    :raises ValueError: If the string is not a valid email address.
    """
    # https://stackoverflow.com/questions/15578019/how-to-check-that-the-string-is-email
    pattern = re.compile(r'^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4}$', re.IGNORECASE)
    if not re.fullmatch(pattern, email_string):
        raise ValueError(f"'{email_string}' is not a valid email address")

    return email_string


def validate_filepaths(filepaths: Iterable[str]) -> list[pathlib.Path]:
    """Checks that all specified filepaths exist on the user's system.

    :param filepaths: All filepaths to be validated
    :return: A list of ``pathlib.Path`` objects for each filepath.
    :raises FileNotFoundError: If any of the filepaths do not exist.
    """
    invalid_paths = [
        filepath for filepath in filepaths if not os.path.isfile(filepath)
    ]

    if invalid_paths:
        raise FileNotFoundError(
            "The following files specified to be attached to the email, do no exist: " +
            ", ".join(invalid_paths)
        )

    return [pathlib.Path(filepath) for filepath in filepaths]


def smtp_connect(hostname: str, port_number: int) -> smtplib.SMTP:
    """Connect to the SMTP server at location ``server_address``:``port_number``.

    :param hostname: The SMTP server's hostname.
    :param port_number: The port number the SMTP server is running on.
    :return: A connection to the SMTP server.
    """
    try:
        smtp_connection = smtplib.SMTP(hostname, port_number, timeout=2)
    except socket.gaierror as error:
        message = f"It appears that {hostname} is not a valid hostname."
        logger.error(error)
        logger.error(message)
        sys.exit(message)
    except (OSError, TimeoutError, ConnectionRefusedError) as error:
        message = (f"Failed to connect to {hostname}:{port_number}.\n" +
                   "Potentially either the hostname or port number are incorrect.")
        logger.error(error)
        logger.error(message)
        sys.exit(message)

    logger.info("Successfully made connection to %s:%d",
                hostname, port_number)

    return smtp_connection


def draft_email(
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


def main() -> None:
    with open("config.toml", "rb") as config_file:
        config = tomllib.load(config_file)

    email_config: dict[str, Any] = config["email"]
    server_config: dict[str, Any] = config["server"]

    with open(email_config["mailing_list"]) as mailing_list_file:
        mailing_list = mailing_list_file.read().splitlines()

    with open(email_config["email_content"]) as email_content_file:
        email_body = email_content_file.read()

    try:
        sender = validate_email(email_config["sender"])
    except ValueError as error:
        logger.error(str(error))
        sys.exit(str(error))

    logger.info("Emails being sent as %s", sender)

    subject: str = email_config["subject"]

    try:
        attachments = validate_filepaths(email_config["attachments"])
    except FileNotFoundError as error:
        logger.error(str(error))
        sys.exit(str(error))

    server_address: str = server_config["hostname"]
    port_number: int = server_config["port_number"]

    with smtp_connect(server_address, port_number) as smtp_connection:
        for recipient in mailing_list:
            logger.info("Sending report to %s", recipient)
            message = draft_email(
                sender, (recipient,), subject, email_body, attachments
            )
            try:
                smtp_connection.send_message(message)
            except (smtplib.SMTPRecipientsRefused, smtplib.SMTPSenderRefused) as error:
                error_message = str(error).strip("{}")
                logger.error(error_message)
                sys.exit(error_message)

            logger.info("Email successfully sent to %s", recipient)


if __name__ == "__main__":
    configure_logging()
    main()
