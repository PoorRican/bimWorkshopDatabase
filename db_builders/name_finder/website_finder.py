from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import Runnable
from langchain_openai import ChatOpenAI

from db_builders.name_finder.base_finder import BaseFinder
from db_builders.utils import filter_results

_WEBSITE_CHECKER_PROMPT = PromptTemplate.from_template(
    """You will be given a list of search results for a manufacturer company named {manufacturer}.
    
Your job is to determine which site is the website for {manufacturer}.

Search Results:
{search_results}

Return the URL of the {manufacturer}'s website.""")


class WebsiteFinder(BaseFinder):
    """ Functor which accepts a manufacturer name and finds the manufacturer website. """
    _chain: Runnable

    def __init__(self, llm: ChatOpenAI):
        super().__init__()

        self._chain = _WEBSITE_CHECKER_PROMPT | llm | StrOutputParser()

    async def __call__(self, manufacturer_name: str) -> str:
        """ Accept a manufacturer name then search for the products page for the manufacturer's website.

        Parameters:
            manufacturer_name: Manufacturer name to search for

        Returns:
            Products page URL for the manufacturer's website
        """
        query = f"{manufacturer_name} manufacturer website"
        results = await self.perform_search(query, 50)

        results = filter_results(results)

        return await self._determine_url(results, manufacturer_name)
