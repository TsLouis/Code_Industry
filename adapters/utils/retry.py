import asyncio
from functools import wraps
from typing import TypeVar, Callable, Any

T = TypeVar("T")

def async_retry(
    retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,)
):
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            retry_count = 0
            current_delay = delay

            while True:
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    retry_count += 1
                    if retry_count > retries:
                        raise e

                    await asyncio.sleep(current_delay)
                    current_delay *= backoff

        return wrapper
    return decorator 