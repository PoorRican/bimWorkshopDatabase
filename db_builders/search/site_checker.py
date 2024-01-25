from langchain.schema.runnable import Runnable
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

from db_builders.utils import retry_on_ratelimit

_DESCRIPTION_EXPAND_PROMPT = PromptTemplate.from_template(
    """ You will be given the title, URL, and description of a search result.

Here is the title: {title}
Here is the URL: {url}
Here is the description: {description}

Please explain what this page is about in one paragraph.
Does this page directly represent a single manufacturing company?
"""
)

_IS_MANUFACTURER_PROMPT = PromptTemplate.from_template(
    """Given an explanation of a search result, determine if it directly represents a webpage for a singular manufacturing company.

"{explanation}"

Return 'manufacturer' if it directly represents a manufacturing company website,
and 'not manufacturer' if it does not directly represent a manufacturing company website.
"""
)


class SiteChecker(object):
    """ Functor which checks if a search result is a valid site by examining the `title`, `url`, and `description`.
    """
    _chain: Runnable

    def __init__(self, llm: ChatOpenAI):
        expand_chain = _DESCRIPTION_EXPAND_PROMPT | llm | StrOutputParser()
        self._chain = {'explanation': expand_chain} | _IS_MANUFACTURER_PROMPT | llm | StrOutputParser()

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
    async def __call__(self, title: str, url: str, description: str) -> bool:
        """ Check if a site is a manufacturer site.

        Parameters:
            title: Title of the search result
            url: URL of the search result
            description: Description of the search result

        Returns:
            True if site is a manufacturer site, False otherwise
        """
        response = await self._chain.ainvoke({'title': title, 'url': url, 'description': description})
        return self.is_manufacturer(response)
