import functools
import time

from loguru import logger


def log_calls(level="INFO", show_result=False):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            func_name = func.__name__
            logger.log(level, f"Calling {func_name}")
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                elapsed = time.time() - start_time
                if show_result:
                    logger.log(
                        level, f"{func_name} completed in {elapsed:.3f}s → {result}"
                    )
                else:
                    logger.log(level, f"{func_name} completed in {elapsed:.3f}s")
                return result
            except Exception as e:
                elapsed = time.time() - start_time
                logger.error(f"{func_name} failed in {elapsed:.3f}s: {e}")
                raise

        return wrapper

    return decorator
