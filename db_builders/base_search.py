import os
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

    async def perform_search(self, query: str, num_results: int = 100) -> list[SearchResultItem]:
        """ Perform a search using the Google custom search API

        Parameters:
            `query`: The query string which will be used to search.
            `num_results`: The number of results to return. Defaults to 100.

        Returns:
            A list of `SearchResultItem` objects.
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
                    if resp.status != 200:
                        print(f"Got status code {resp.status} from Google API.")
                        print(await resp.text())
                        continue
                    # repeat search if 5XX error is returned
                    if 500 <= resp.status < 600:
                        print(f"Got status code {resp.status} from Google API. Retrying after 30 secs...")
                        await sleep(30)
                        await self.perform_search(query, num_results)
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
