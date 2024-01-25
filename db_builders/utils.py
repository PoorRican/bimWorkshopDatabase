import asyncio
import functools

from openai import RateLimitError


def retry_on_ratelimit():
    """ Decorator which retries an asynchronous OpenAI call if a RateLimitError is raised. """
    def decorator(func):
        @functools.wraps(func)
        async def wrapped(*args, **kwargs):
            while True:
                try:
                    result = await func(*args, **kwargs)
                except RateLimitError:
                    await asyncio.sleep(15)
                except Exception as e:
                    raise e from None
                else:
                    break
            return result
        return wrapped
    return decorator
