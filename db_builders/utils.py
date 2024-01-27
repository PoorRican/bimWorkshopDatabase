import asyncio
import functools
from urllib.parse import urlparse

from openai import RateLimitError, InternalServerError, APIConnectionError, APITimeoutError, APIResponseValidationError


def retry_on_ratelimit():
    """ Decorator which retries an asynchronous OpenAI call if a RateLimitError or any other openai error is raised. """
    def decorator(func):
        @functools.wraps(func)
        async def wrapped(*args, **kwargs):
            while True:
                try:
                    result = await func(*args, **kwargs)
                except RateLimitError:
                    await asyncio.sleep(15)
                except (InternalServerError, APIConnectionError, APITimeoutError, APIResponseValidationError):
                    pass
                except Exception as e:
                    raise e from None
                else:
                    break
            return result
        return wrapped
    return decorator


def print_bar(text: str):
    length = len(text)
    bar = "=" * length

    print(bar)
    print(text)
    print(bar)


def strip_url(url: str) -> str:
    """ Strip URL down to the base URL

    Parameters:
        url: URL to strip

    Returns:
        URL with all paths, query parameters, fragments and path removed

    Examples:
        >>> strip_url('https://www.example.com/this/path/should/be/stripped?param1=1&param2=2#fragment')
        'https://www.example.com'

        No error is raised if the URL is already at the base:
        >>> strip_url('https://www.example.com')
        'https://www.example.com'
    """
    return (urlparse(url)
            ._replace(path='')
            ._replace(params='')
            ._replace(query='')
            ._replace(fragment='')
            .geturl())
