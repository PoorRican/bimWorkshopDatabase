import asyncio
from typing import List

from googlesearch import search
from langchain_openai import ChatOpenAI

from db_builders.typedefs import Manufacturer
from .name_extractor import NameExtractor
from .site_checker import SiteChecker
from .utils import strip_url


class SearchHandler(object):
    """ Functor which conducts a search of manufacturers and returns the results which represent companies. """
    _site_checker: SiteChecker
    _name_extractor: NameExtractor

    def __init__(self, llm: ChatOpenAI):
        self._site_checker = SiteChecker(llm)
        self._name_extractor = NameExtractor(llm)

    async def __call__(self, omniclass_name: str, num_results: int = 1000) -> List[Manufacturer]:
        """ Conduct a search of manufacturers and return the results which represent companies.

        Parameters:
            omniclass_name: Query to search for

        Returns:
            List of manufacturers objects which offer the given omniclass_name
        """
        # TODO: implement catching of 429 errors

        # get search results
        search_query = f"{omniclass_name} manufacturers"

        results = []    # all search results
        tasks = []      # tasks for verifying site
        for result in search(search_query,
                             sleep_interval=60,
                             num_results=num_results,
                             advanced=True,
                             lang='en'):
            results.append(result)
            tasks.append(self._site_checker(result.title, result.url, result.description))

        print("Finished search. Awaiting validation of sites.")

        # join all tasks into a tuple of bool values
        valid_sites = await asyncio.gather(*tasks)

        # filter out non-manufacturer sites and extract names
        urls = []
        name_tasks = []
        for result, is_manufacturer in zip(results, valid_sites):
            if is_manufacturer:
                name_tasks.append(self._name_extractor(result.title, result.url, result.description))
                urls.append(result.url)

        manufacturer_names = await asyncio.gather(*name_tasks)

        # create manufacturer objects
        manufacturers = []
        for name, url in zip(manufacturer_names, urls):
            stripped_url = strip_url(url)
            manufacturers.append(Manufacturer(name, stripped_url))

        print(f"Found valid {len(manufacturers)} manufacturer sites!")

        return manufacturers
