import functools
import time


def retry(max_attempts=3, delay=0.5, backoff=1.5):
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            last = None
            wait = delay
            for attempt in range(max_attempts):
                try:
                    return fn(*args, **kwargs)
                except Exception as e:
                    last = e
                    if attempt < max_attempts - 1:
                        time.sleep(wait)
                        wait *= backoff
            raise last
        return wrapper
    return decorator
