import asyncio
import functools
from urllib.parse import urlparse

from openai import RateLimitError, InternalServerError, APIConnectionError, APITimeoutError, APIResponseValidationError

from db_builders.typedefs import SearchResultItem


# List of keywords to exclude from search results
EXCLUDE_LIST = ['amazon', 'china', 'india', 'co.uk', '.cn', '.in', 'ebay', 'lowes', 'homedepot', 'walmart',
                'target.com', '.gov', 'acehardware', 'business', 'news', 'alibaba', 'aliexpress', 'wikipedia',
                'youtube', 'facebook', 'twitter', 'instagram', 'pinterest', 'linkedin', 'yelp', 'bbb', 'glassdoor',
                'biz', 'bloomberg', 'forbes.com', 'fortune.com', 'inc', 'investopedia', 'money', 'nasdaq', 'nyse',
                'reuters', 'seekingalpha', 'stocktwits', 'thestreet', 'wsj', 'yahoo', 'yahoofinance', 'zacks.com',
                'barrons.com', 'bloomberg', 'cnbc', 'cnn', 'foxbusiness', 'marketwatch', 'msn', 'newsmax', 'npr',
                'samsclub', 'costco', 'overstock', 'sears', 'kmart', 'wayfair', 'etsy']


def retry_on_ratelimit():
    """ Decorator which retries an asynchronous OpenAI call if a RateLimitError or any other openai error is raised. """
    def decorator(func):
        @functools.wraps(func)
        async def wrapped(*args, **kwargs):
            while True:
                try:
                    result = await func(*args, **kwargs)
                except RateLimitError:
                    await asyncio.sleep(10)
                except (InternalServerError, APIConnectionError, APITimeoutError, APIResponseValidationError) as e:
                    print(e)
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


def filter_results(results: list[SearchResultItem]) -> list[SearchResultItem]:
    """ Filter out irrelevant search results from a list of search results.

    This uses a list of keywords to exclude irrelevant search results.

    Parameters:
        results: List of search results to filter

    Returns:
        List of valid `SearchResultItem` objects
    """
    return [result for result in results if not any(word in result.link for word in EXCLUDE_LIST)]
