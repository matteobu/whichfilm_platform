"""Reusable decorators for contrib modules."""

import time
import functools
from typing import Callable, Any


def retry(max_attempts=3, delay=1, backoff=2):
    """
    Retry decorator with exponential backoff.

    Args:
        max_attempts (int): Maximum number of retry attempts
        delay (int): Initial delay between retries in seconds
        backoff (float): Backoff multiplier for each retry

    Example:
        @retry(max_attempts=3, delay=1)
        def fetch_data():
            ...
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            current_delay = delay
            last_exception = None

            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        print(f"Attempt {attempt + 1} failed: {e}. Retrying in {current_delay}s...")
                        time.sleep(current_delay)
                        current_delay *= backoff

            raise last_exception

        return wrapper
    return decorator


def cached(ttl=3600):
    """
    Cache decorator with time-to-live.

    Args:
        ttl (int): Time-to-live in seconds

    Example:
        @cached(ttl=3600)
        def get_expensive_data():
            ...
    """
    def decorator(func: Callable) -> Callable:
        cache = {}
        cache_time = {}

        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            key = (args, tuple(sorted(kwargs.items())))
            now = time.time()

            if key in cache and (now - cache_time[key]) < ttl:
                return cache[key]

            result = func(*args, **kwargs)
            cache[key] = result
            cache_time[key] = now
            return result

        return wrapper
    return decorator
