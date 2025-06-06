import logging
import time
import uuid
from functools import wraps

logger = logging.getLogger(__name__)


def stopwatch(action: str):
    """Decorator to measure the execution time of a task."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger.info(f"============ Starting timer for {action} ===============")
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error in {action}: {e}")
                raise e
            finally:
                end_time = time.time()
                elapsed_time = end_time - start_time
                logger.info(f"Elapsed time for {action}: {elapsed_time:.4f} seconds")
                logger.info(f"============ Ending timer for {action} ===============")
            return result

        return wrapper

    return decorator


def is_valid_uuid4(uuid_string):
    """
    Validate that a UUID string is a valid UUID4.

    Parameters
    ----------
    uuid_string : str
        The UUID string to validate.

    Returns
    -------
    bool
        True if uuid_string is a valid UUID4, False otherwise.
    """
    try:
        val = uuid.UUID(uuid_string, version=4)
    except ValueError:
        return False

    # Ensure the string matches the canonical form of a UUID4
    return str(val) == uuid_string
