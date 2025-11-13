import functools
import time

from loguru import logger


def retry(max_retries: int = 3, delay_seconds: int = 300):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries + 1):
                try:
                    if attempt > 0:
                        logger.warning(
                            f"Retry attempt {attempt}/{max_retries} "
                            f"for {func.__name__} "
                            f"after {delay_seconds}s delay"
                        )
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    logger.error(
                        f"Error in {func.__name__} "
                        f"(attempt {attempt + 1}/{max_retries + 1}): {e}"
                    )
                    if attempt < max_retries:
                        logger.info(
                            f"Waiting {delay_seconds} seconds before retry"
                            f"(attempt {attempt + 1}/{max_retries + 1})"
                        )
                        time.sleep(delay_seconds)
            logger.error(
                f"All {max_retries + 1} attempts failed for {func.__name__}. "
                f"Raising last exception."
            )
            raise last_exception

        return wrapper

    return decorator
