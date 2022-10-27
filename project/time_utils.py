import signal
import timeit
from contextlib import contextmanager


__all__ = ["TimeoutException", "time_limit", "timeit_with_time_limit"]


class TimeoutException(Exception):
    pass


@contextmanager
def time_limit(seconds):
    def signal_handler(signum, frame):
        raise TimeoutException("Timed out!")

    signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)


def timeit_with_time_limit(timed_fun, time_limit_secs) -> float:
    try:
        with time_limit(time_limit_secs):
            return timeit.timeit(timed_fun, number=1)
    except TimeoutException as e:
        return float("inf")
