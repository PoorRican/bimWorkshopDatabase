import asyncio
from typing import List

from langchain_openai import ChatOpenAI

from db_builders.typedefs import Manufacturer
from db_builders.utils import strip_url
from .base_search import BaseSearchHandler
from .manufacturer_checker import SiteDoubleChecker
from .name_extractor import NameExtractor
from .site_checker import SiteChecker


class SearchHandler(BaseSearchHandler):
    """ Functor which conducts a search of manufacturers and returns the results which represent companies. """
    _site_checker: SiteChecker
    _name_extractor: NameExtractor
    _site_verifier: SiteDoubleChecker

    def __init__(self, llm: ChatOpenAI):
        super().__init__()

        self._site_checker = SiteChecker(llm)
        self._name_extractor = NameExtractor(llm)
        self._site_verifier = SiteDoubleChecker(llm)

    @staticmethod
    def _deduplicate_manufacturers(results: list[Manufacturer]) -> list[Manufacturer]:
        """ Deduplicate manufacturers based on URL

        Parameters:
            results: List of manufacturers to deduplicate

        Returns:
            List of manufacturers with duplicates removed
        """
        urls = []
        deduplicated_results = []
        for result in results:
            if result.url not in urls:
                urls.append(result.url)
                deduplicated_results.append(result)

        return deduplicated_results

    async def __call__(self, omniclass_name: str, num_results: int = 1000) -> List[Manufacturer]:
        """ Conduct a search of manufacturers and return the results which represent companies.

        Parameters:
            omniclass_name: Query to search for

        Returns:
            List of manufacturers objects which offer the given omniclass_name
        """

        # get search results
        search_query = f"{omniclass_name} manufacturers"

        print("\u2514 Performing search... ")
        results = await self.perform_search(search_query, num_results)

        print(f"  - Got {len(results)} results.")

        # perform a keyword filter to remove irrelevant results
        exclude = ['amazon', 'china', 'india', 'co.uk', '.cn', '.in', 'ebay', 'lowes', 'homedepot', 'walmart',
                   'target.com', '.gov', 'acehardware', 'business', 'news', 'alibaba', 'aliexpress', 'wikipedia',
                   'youtube', 'facebook', 'twitter', 'instagram', 'pinterest', 'linkedin', 'yelp', 'bbb', 'glassdoor',
                   'biz', 'bloomberg', 'forbes.com', 'fortune.com', 'inc', 'investopedia', 'money', 'nasdaq', 'nyse',
                   'reuters', 'seekingalpha', 'stocktwits', 'thestreet', 'wsj', 'yahoo', 'yahoofinance', 'zacks.com',
                   'barrons.com', 'bloomberg', 'cnbc', 'cnn', 'foxbusiness', 'marketwatch', 'msn', 'newsmax', 'npr',]
        results = [result for result in results if not any(word in result.link for word in exclude)]

        print(f"  - Filtered results down to {len(results)}")

        # check if each site is a manufacturer in batches of 10
        print("\u2514 Checking if each site is a manufacturer... ")

        valid_sites = []
        batch_size = 5
        for i in range(0, len(results), batch_size):
            print(f"  - Checking batch {i // batch_size + 1} of {len(results) // batch_size + 1}")
            tasks = []
            for result in results[i:i + batch_size]:
                tasks.append(self._site_checker(result.title, result.link, result.snippet))
            valid_sites.extend(await asyncio.gather(*tasks))

        print("  - Done!")

        # filter out non-manufacturer sites and extract names
        print("\u2514 Extracting names from manufacturer sites... ")

        urls = []
        name_tasks = []
        for result, is_manufacturer in zip(results, valid_sites):
            if is_manufacturer:
                name_tasks.append(self._name_extractor(result.title, result.link, result.snippet))
                urls.append(result.link)

        manufacturer_names = await asyncio.gather(*name_tasks)

        print("  \u2514 Done!")

        # create manufacturer objects
        print("\u2514 Creating manufacturer objects and deduplicating results... ")

        manufacturers = []
        for name, url in zip(manufacturer_names, urls):
            stripped_url = strip_url(url)
            manufacturers.append(Manufacturer(name, stripped_url))

        # deduplicate manufacturers
        manufacturers = self._deduplicate_manufacturers(manufacturers)

        print("  \u2514 Done")

        # double check that manufacturers are valid
        print("\u2514 Double checking manufacturers... ")
        tasks = []
        for manufacturer in manufacturers:
            tasks.append(self._site_verifier(manufacturer.url))

        valid_manufacturers = await asyncio.gather(*tasks)

        print("  \u2514 Validated sites!")

        manufacturers = [manufacturer for manufacturer, is_valid in zip(manufacturers, valid_manufacturers) if is_valid]

        print("\u2514 Returning manufacturers.")

        return manufacturers
