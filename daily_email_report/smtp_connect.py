import logging
import smtplib
import socket
import sys


logger = logging.getLogger(__name__)


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
