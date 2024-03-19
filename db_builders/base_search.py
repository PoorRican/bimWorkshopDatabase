import os
import warnings
from asyncio import sleep
from typing import ClassVar

import aiohttp
from dotenv import load_dotenv

from db_builders.typedefs import SearchResultItem

load_dotenv()

BASE_URL = 'https://www.googleapis.com/customsearch/v1'
API_KEY = os.getenv('GOOGLE_SEARCH_API_KEY')
SEARCH_ENGINE_ID = os.getenv('GOOGLE_SEARCH_ENGINE_ID')

# check that environment variables are properly set
if API_KEY is None:
    raise ValueError("GOOGLE_SEARCH_API_KEY is not set!")
if SEARCH_ENGINE_ID is None:
    raise ValueError("GOOGLE_SEARCH_ENGINE_ID is not set!")


class BaseSearchHandler:
    """ Base class for search handlers.

    This class contains a method for performing a search using the Google custom search API.
    """
    HEADERS: ClassVar[dict] = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                                             'AppleWebKit/537.36 (KHTML, like Gecko) '
                                             'Chrome/120.0.0.0 Safari/537.36'
                               }
    retry_count: int
    MAX_RETRY_COUNT: ClassVar[int] = 5

    def __init__(self):
        self.retry_count = 0

    async def perform_search(self, query: str, num_results: int = 100) -> list[SearchResultItem]:
        """ Perform a search using the Google custom search API

        # Status code handlers:
        - If the status code is 4XX or 5XX, the search will be retried up to 3 times.
        - If the status code is not 200, 4XX, or 5XX, the status code will be printed and the search will be skipped.

        Parameters:
            `query`: The query string which will be used to search.
            `num_results`: The number of results to return. Defaults to 100.

        Returns:
            A list of `SearchResultItem` objects.

            However, if an error occurs and cannot be resolved, an empty list will be returned. Errors include
            4XX or 5XX status codes (after a retry limit has been hit), or if the response does not contain the expected
            data.
        """
        results = []

        # if `num_results` is less than 10, force one page
        if num_results > 10:
            pages = num_results // 10
        else:
            pages = 1

        async with aiohttp.ClientSession(headers=self.HEADERS) as session:
            for page in range(pages):
                start = page * 10 + 1
                # doc: https://developers.google.com/custom-search/v1/using_rest
                url = f"{BASE_URL}?key={API_KEY}&cx={SEARCH_ENGINE_ID}&q={query}&start={start}"

                if num_results < 10:
                    url += f"&num={num_results}"

                async with session.get(url) as resp:
                    # repeat search if 429 or 5XX error is returned
                    if 500 <= resp.status < 600 or resp.status == 429:
                        if self.retry_count >= self.MAX_RETRY_COUNT:
                            print(await resp.text())
                            raise RuntimeError(f"Got status code {resp.status} from Google API. "
                                               f"Retried {self.retry_count} times. Skipping...")
                        self.retry_count += 1
                        await sleep(15)
                        await self.perform_search(query, num_results)
                    if resp.status != 200:
                        raise RuntimeError(f"Got status code {resp.status} from Google API.")

                    self.retry_count = 0

                    data = await resp.json()
                    try:
                        items = data['items']
                        for item in items:
                            results.append(
                                SearchResultItem(
                                    title=item['title'],
                                    link=item['link'],
                                    snippet=item['snippet']
                                ))
                    except KeyError:
                        # no results
                        pass
        return results
