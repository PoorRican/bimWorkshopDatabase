import os

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
    _session: aiohttp.ClientSession

    def __init__(self):
        # setup aiohttp session
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/120.0.0.0 Safari/537.36'
        }
        self._session = aiohttp.ClientSession(headers=headers)

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
        for page in range(pages):
            start = page * 10 + 1
            # doc: https://developers.google.com/custom-search/v1/using_rest
            url = f"{BASE_URL}?key={API_KEY}&cx={SEARCH_ENGINE_ID}&q={query}&start={start}"
            async with self._session.get(url) as resp:
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

