from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import Runnable
from langchain_openai import ChatOpenAI

from db_builders.search.base_search import BaseSearchHandler
from db_builders.utils import retry_on_ratelimit

load_dotenv()

_CHECK_SEARCH_RESULTS_PROMPT = PromptTemplate.from_template(
    """You will be given a list of search results for a single website.
    
Determine if this website directly represents a manufacturer website.

Search Results:
{search_results}

Return 'manufacturer' if it directly represents a manufacturing company website,
and 'not manufacturer' if it does not directly represent a manufacturing company website.
"""
)


class SiteDoubleChecker(BaseSearchHandler):
    _chain: Runnable

    def __init__(self, llm: ChatOpenAI):
        super().__init__()

        self._chain = _CHECK_SEARCH_RESULTS_PROMPT | llm | StrOutputParser()

    @staticmethod
    def is_manufacturer(response: str) -> bool:
        """ Detect if site is a manufacturer site based on search result.

        This is parse the result from `_chain`.

        Parameters:
            response: LLM response from `_chain`

        Returns:
            True if site is a manufacturer site, False otherwise
        """
        if 'not manufacturer' in response.lower():
            return False
        elif 'manufacturer' in response.lower():
            return True
        else:
            raise ValueError(f"Invalid response from LLM: {response}")

    @retry_on_ratelimit()
    async def _check(self, results: str) -> bool:
        """ Check if a site is a manufacturer site.

        Parameters:
            results: Search results to check

        Returns:
            True if site is a manufacturer site, False otherwise
        """
        response = await self._chain.ainvoke({'search_results': results})
        return self.is_manufacturer(response)

    async def __call__(self, site: str) -> bool:
        """ Check if a site is a manufacturer site.

        Parameters:
            site: Site to check

        Returns:
            True if site is a manufacturer site, False otherwise
        """
        query = f"what is {site} site:{site}"
        results = await self.perform_search(query, num_results=5)

        # format search results
        formatted_results = ""
        for result in results:
            formatted_results += f"Title: {result.title}\nURL: {result.link}\nDescription: {result.snippet}\n\n"

        return await self._check(formatted_results)
