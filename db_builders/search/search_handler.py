import asyncio
import os
from typing import List

import aiohttp
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from db_builders.typedefs import Manufacturer, SearchResultItem
from db_builders.utils import strip_url
from .name_extractor import NameExtractor
from .site_checker import SiteChecker

load_dotenv()

BASE_URL = 'https://www.googleapis.com/customsearch/v1'
API_KEY = os.getenv('GOOGLE_SEARCH_API_KEY')
SEARCH_ENGINE_ID = os.getenv('GOOGLE_SEARCH_ENGINE_ID')

# check that environment variables are properly set
if API_KEY is None:
    raise ValueError("GOOGLE_SEARCH_API_KEY is not set!")
if SEARCH_ENGINE_ID is None:
    raise ValueError("GOOGLE_SEARCH_ENGINE_ID is not set!")


class SearchHandler(object):
    """ Functor which conducts a search of manufacturers and returns the results which represent companies. """
    _site_checker: SiteChecker
    _name_extractor: NameExtractor
    _session: aiohttp.ClientSession

    def __init__(self, llm: ChatOpenAI):
        self._site_checker = SiteChecker(llm)
        self._name_extractor = NameExtractor(llm)

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
                                mime=item['mime'],
                                snippet=item['snippet']
                            ))
                except KeyError:
                    # no results
                    pass
        return results

    async def __call__(self, omniclass_name: str, num_results: int = 1000) -> List[Manufacturer]:
        """ Conduct a search of manufacturers and return the results which represent companies.

        Parameters:
            omniclass_name: Query to search for

        Returns:
            List of manufacturers objects which offer the given omniclass_name
        """

        # get search results
        search_query = f"{omniclass_name} manufacturers"

        results = await self.perform_search(search_query, num_results)
        tasks = []      # tasks for verifying site
        for result in results:
            tasks.append(self._site_checker(result.title, result.link, result.snippet))

        print("Finished search. Awaiting validation of sites.")

        # join all tasks into a tuple of bool values
        valid_sites = await asyncio.gather(*tasks)

        # filter out non-manufacturer sites and extract names
        urls = []
        name_tasks = []
        for result, is_manufacturer in zip(results, valid_sites):
            if is_manufacturer:
                name_tasks.append(self._name_extractor(result.title, result.link, result.snippet))
                urls.append(result.link)

        manufacturer_names = await asyncio.gather(*name_tasks)

        # create manufacturer objects
        manufacturers = []
        for name, url in zip(manufacturer_names, urls):
            stripped_url = strip_url(url)
            manufacturers.append(Manufacturer(name, stripped_url))

        print(f"Found valid {len(manufacturers)} manufacturer sites!")

        return manufacturers
