from typing import Any
import functools
import datetime
import logging
import tomllib

from .smtp_connect import deliver_to_mailing_list
from .task_scheduler import schedule_daily_task
from .logging_config import configure_logging
from .draft_email import draft_email

logger = logging.getLogger(__name__)


def main():
    configure_logging()

    with open("config.toml", "rb") as config_file:
        config = tomllib.load(config_file)

    email_config: dict[str, Any] = config["email"]
    server_config: dict[str, Any] = config["server"]
    schedule_time: datetime.time = config["schedule_time"]

    with open(email_config["mailing_list"]) as mailing_list_file:
        mailing_list = mailing_list_file.read().splitlines()

    message = draft_email(email_config)

    hostname: str = server_config["hostname"]
    port_number: int = server_config["port_number"]

    task = functools.partial(deliver_to_mailing_list,
                             hostname, port_number, mailing_list, message)

    schedule_daily_task(task, schedule_time.hour, schedule_time.minute)
