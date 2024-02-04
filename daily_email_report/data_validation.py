from collections.abc import Iterable
import pathlib
import logging
import re
import os


logger = logging.getLogger(__name__)


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
