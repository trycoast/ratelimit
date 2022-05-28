"""
Rate limit public interface.

This module includes the decorator used to rate limit function invocations.
Additionally this module includes a naive retry strategy to be used in
conjunction with the rate limit decorator.
"""
import threading
import time
from functools import wraps

from ratelimit.exception import RateLimitException
from ratelimit.utils import now


class RateLimitDecorator:
    """
    Rate limit decorator class.
    """

    def __init__(self, duration: int = 1, burst: int = 1,
                 sleep: bool = False, clock=now(), raise_on_limit=True):
        """
        Instantiate a RateLimitDecorator with some sensible defaults. By
        default, the Twitter rate limiting window is respected (15 calls every
        15 minutes).

        :param float duration: An upper bound time period (in seconds) between calls.
        :param bool sleep: Will sleep and retry else throw an exception.
        :param function clock: An optional function retuning the current time.
        :param bool raise_on_limit: A boolean allowing the caller to avoid raising an exception.
        :param int burst: The number of calls allowed in a burst.
        """
        self.duration = duration
        self.sleep = sleep
        self.clock = clock
        self.raise_on_limit = raise_on_limit
        self.burst = burst
        self.burst_max = burst

        # Initialise the decorator state.
        self.last_reset = duration
        self.num_calls = 0

        # Add thread safety.
        self.lock = threading.RLock()

    def __call__(self, func):
        '''
        Return a wrapped function that prevents further function invocations if
        previously called within a specified period of time.

        :param function func: The function to decorate.
        :return: Decorated function.
        :rtype: function
        '''
        @wraps(func)
        def wrapper(*args, **kargs):
            '''
            Extend the behaviour of the decorated function, forwarding function
            invocations previously called no sooner than a specified period of
            time. The decorator will raise an exception if the function cannot
            be called so the caller may implement a retry strategy such as an
            exponential backoff.

            :param args: non-keyword variable length argument list to the decorated function.
            :param kargs: keyworded variable length argument list to the decorated function.
            :raises: RateLimitException
            '''
            with self.lock:
                period_remaining = self.__period_remaining()

                # replenish bursts (cap to burst_max)
                self.burst += (self.clock() - self.last_reset) * 1 / self.duration
                self.burst = self.burst_max if self.burst > self.burst_max else self.burst

                if period_remaining > 0 and int(self.burst) == 0:
                    if self.sleep:
                        time.sleep(period_remaining)
                    elif self.raise_on_limit:
                        raise RateLimitException('too many calls', period_remaining)

                self.burst = self.burst - 1 if self.burst >= 1 else 0   # decrement one call from burst.
                self.last_reset = self.clock()                          # reset the last time method was called.

            return func(*args, **kargs)
        return wrapper

    def __period_remaining(self):
        '''
        Return the period remaining for the current rate limit window.

        :return: The remaing period.
        :rtype: float
        '''

        elapsed = self.clock() - self.last_reset
        return self.duration - elapsed
