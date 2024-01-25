from langchain_openai import ChatOpenAI

from db_builders.search.search_handler import SearchHandler
from db_builders.typedefs import Manufacturer, OmniClass


async def _search_for_manufacturers(omniclasses: list[OmniClass],
                                    llm: ChatOpenAI,
                                    num_results: int = 1000) -> dict[str, list[Manufacturer]]:
    handler = SearchHandler(llm)

    manufacturer_results = {}
    for omniclass in omniclasses:
        name = omniclass.name
        results = await handler(name, num_results)
        manufacturer_results[name] = results

    return manufacturer_results
