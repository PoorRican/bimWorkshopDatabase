import re
import warnings
from abc import ABC
from langchain_core.runnables import Runnable

from db_builders.base_search import BaseSearchHandler
from db_builders.typedefs import SearchResultItem
from db_builders.utils import retry_on_ratelimit


class BaseFinder(BaseSearchHandler, ABC):
    """ Functor which accepts a URL then finds the products page. """
    _chain: Runnable

    @staticmethod
    def _format_results(results: list[SearchResultItem]) -> str:
        """ Format the results

        Parameters:
            results: List of manufacturer website URLs

        Returns:
            List of manufacturer website URLs
        """
        return "\n".join([f"{result.link}" for result in results])

    @staticmethod
    def _extract_url(response: str) -> str:
        """ Extract the URL from the response.

        Parameters:
            response: LLM response from `_chain`

        Returns:
            Manufacturer website URL
        """
        url_pattern = re.compile(r'https://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
        urls = re.findall(url_pattern, response)
        try:
            return urls[0]
        except IndexError:
            warnings.warn("Could not find URL")
            return ''

    @retry_on_ratelimit()
    async def _determine_url(self, results: list[SearchResultItem], manufacturer: str) -> str:
        """ Determine the manufacturer's website URL.

        Parameters:
            results: List of search results
            manufacturer: Manufacturer name

        Returns:
            Manufacturer website URL
        """
        formatted_results = self._format_results(results)
        response = await self._chain.ainvoke({'search_results': formatted_results, 'manufacturer': manufacturer})

        return self._extract_url(response)

