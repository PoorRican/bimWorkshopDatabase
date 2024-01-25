import asyncio

from langchain.schema.runnable import Runnable
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from openai import RateLimitError

_PROMPT = PromptTemplate.from_template(
    """You will be given the title, description, and URL of a company website.

Here is the website title: {title}
Here is the website description: {description}
Here is the website URL: {url}

Infer and extract the name of the company. Only return the name of the company.
"""
)


class NameExtractor(object):
    _chain: Runnable

    def __init__(self, llm: ChatOpenAI):
        self._chain = _PROMPT | llm | StrOutputParser()

    @staticmethod
    def _clean_text(name: str) -> str:
        """ Remove GPT artifacts from the output.

        GPT has a tendency to:
        - add the string "The name of the company is ..."
        - add a period at the end
        - surround text with quotation marks
        """
        cleaned = name.replace("The name of the company is ", "")
        cleaned = cleaned.replace("\"", "")
        if cleaned[-1] == '.':
            cleaned = cleaned[:-1]

        return cleaned

    async def __call__(self, title: str, url: str, description: str) -> str:
        """ Extract the name of a company from a search result. """
        while True:
            try:
                response = await self._chain.ainvoke({'title': title, 'url': url, 'description': description})
                break
            except RateLimitError:
                print("Rate limit exceeded. Waiting 15 seconds.")
                await asyncio.sleep(15)

        cleaned = self._clean_text(response)
        return cleaned
