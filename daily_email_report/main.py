from typing import Any
import logging
import smtplib
import tomllib
import sys

from .logging_config import configure_logging
from .smtp_connect import smtp_connect
from .draft_email import draft_email

logger = logging.getLogger(__name__)


def main():
    configure_logging()

    with open("config.toml", "rb") as config_file:
        config = tomllib.load(config_file)

    email_config: dict[str, Any] = config["email"]
    server_config: dict[str, Any] = config["server"]

    with open(email_config["mailing_list"]) as mailing_list_file:
        mailing_list = mailing_list_file.read().splitlines()

    message = draft_email(email_config)

    server_address: str = server_config["hostname"]
    port_number: int = server_config["port_number"]

    with smtp_connect(server_address, port_number) as smtp_connection:
        for recipient in mailing_list:
            logger.info("Sending report to %s", recipient)

            del message["To"]
            message["To"] = recipient
            try:
                smtp_connection.send_message(message)
            except (smtplib.SMTPRecipientsRefused, smtplib.SMTPSenderRefused) as error:
                error_message = str(error).strip("{}")
                logger.error(error_message)
                sys.exit(error_message)

            logger.info("Email successfully sent to %s", recipient)
