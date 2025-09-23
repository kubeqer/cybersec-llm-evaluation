import functools

from loguru import logger


def error_handling(default=None, reraise: bool = True):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Exception in {func.__name__}: {e}")
                if reraise:
                    raise
                return default

        return wrapper

    return decorator
