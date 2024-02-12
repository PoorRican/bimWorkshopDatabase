import warnings

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import Runnable
from langchain_openai import ChatOpenAI
import re

from db_builders.base_search import BaseSearchHandler
from db_builders.typedefs import SearchResultItem
from db_builders.utils import retry_on_ratelimit

_WEBSITE_CHECKER_PROMPT = PromptTemplate.from_template(
    """You will be given a list of search results for a manufacturer company named {manufacturer}.
    
Your job is to determine which site is the website for {manufacturer}.

Search Results:
{search_results}

Return the URL of the {manufacturer}'s website.""")


class WebsiteFinder(BaseSearchHandler):
    """ Functor which accepts a manufacturer name then find the products page for the manufacturer website. """
    _chain: Runnable

    def __init__(self, llm: ChatOpenAI):
        super().__init__()

        self._chain = _WEBSITE_CHECKER_PROMPT | llm | StrOutputParser()

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

    async def __call__(self, manufacturer_name: str) -> str:
        """ Accept a manufacturer name then search for the products page for the manufacturer's website.

        Parameters:
            manufacturer_name: Manufacturer name to search for

        Returns:
            Products page URL for the manufacturer's website
        """
        query = f"{manufacturer_name} manufacturer website"
        results = await self.perform_search(query, 10)

        return await self._determine_url(results, manufacturer_name)
