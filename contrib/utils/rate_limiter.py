"""Rate limiting utilities."""

import time
from functools import wraps


class RateLimiter:
    """Simple rate limiter using token bucket algorithm."""

    def __init__(self, calls_per_second=1):
        """
        Initialize rate limiter.

        Args:
            calls_per_second (float): Maximum number of calls per second
        """
        self.calls_per_second = calls_per_second
        self.min_interval = 1.0 / calls_per_second
        self.last_called = 0.0

    def wait_if_needed(self):
        """Wait if necessary to maintain rate limit."""
        now = time.time()
        time_since_last_call = now - self.last_called

        if time_since_last_call < self.min_interval:
            sleep_time = self.min_interval - time_since_last_call
            time.sleep(sleep_time)

        self.last_called = time.time()

    def __call__(self, func):
        """Decorator to rate limit a function."""

        @wraps(func)
        def wrapper(*args, **kwargs):
            self.wait_if_needed()
            return func(*args, **kwargs)

        return wrapper
