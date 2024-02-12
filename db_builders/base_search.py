import os
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

    async def perform_search(self, query: str, num_results: int = 100) -> list[SearchResultItem]:
        """ Perform a search using the Google custom search API

        Parameters:
            `query`: The query string which will be used to search.
            `num_results`: The number of results to return. Defaults to 100.

        Returns:
            A list of `SearchResultItem` objects.
        """
        results = []

        pages = num_results // 10
        async with aiohttp.ClientSession(headers=self.HEADERS) as session:
            for page in range(pages):
                start = page * 10 + 1
                # doc: https://developers.google.com/custom-search/v1/using_rest
                url = f"{BASE_URL}?key={API_KEY}&cx={SEARCH_ENGINE_ID}&q={query}&start={start}"
                async with session.get(url) as resp:
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