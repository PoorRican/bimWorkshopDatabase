from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

from db_builders.name_finder.base_finder import BaseFinder


_WEBSITE_CHECKER_PROMPT = PromptTemplate.from_template(
    """You will be given a list of search results for a manufacturer company named {manufacturer}.

Your job is to determine which URL is the "product page" for {manufacturer}.

Search Results:
{search_results}

Return the product page URL.""")


class ProductPageFinder(BaseFinder):
    """ Functor which accepts a URL then finds the products page. """

    def __init__(self, llm: ChatOpenAI):
        super().__init__()

        self._chain = _WEBSITE_CHECKER_PROMPT | llm | StrOutputParser()

    async def __call__(self, manufacturer_name: str, site: str) -> str:
        """ Accept a manufacturer name then search for the products page for the manufacturer's website.

        Parameters:
            manufacturer_name: Manufacturer name to search for
            site: Manufacturer website

        Returns:
            Products page URL
        """
        query = f"{manufacturer_name} site:{site} products"
        results = await self.perform_search(query, 10)

        return await self._determine_url(results, manufacturer_name)
