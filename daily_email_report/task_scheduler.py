from collections.abc import Callable
import datetime
import sched


def schedule_daily_task(
        task: Callable[[], None],
        hour: int,
        minute: int,
        second: int = 0
) -> None:
    """Schedule the given function to be run at the same time every day.

    Note: Will run forever until manually stopped.
    :param task: The function to be run daily.
    :param hour: The hour of the day to run the function.
    :param minute: The minute of the hour to run the function.
    :param second: The second within the minute to run the function. Defaults to 0.
    """
    while True:
        scheduler = sched.scheduler()

        current_time = datetime.datetime.now()

        next_run_time = (current_time.replace(
            hour=hour, minute=minute, second=second
        ) + datetime.timedelta(days=1)).timestamp()

        scheduler.enterabs(next_run_time, 1, task)
        scheduler.run()
