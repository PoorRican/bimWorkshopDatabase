import asyncio
import csv
from pathlib import Path

from langchain_openai import ChatOpenAI

from db_builders.search.search_handler import SearchHandler
from db_builders.typedefs import Manufacturer, OmniClass


MANUFACTURER_SAVE_PATH = Path('data/manufacturers')


async def _search_for_manufacturers(omniclass: OmniClass,
                                    handler: SearchHandler,
                                    num_results: int = 1000):
    print(f"Getting manufacturers for {omniclass.number} {omniclass.name}")
    results = await handler(omniclass.name, num_results)
    _save_manufacturers(omniclass, results)


def _save_manufacturers(omniclass: OmniClass, manufacturers: list[Manufacturer]):
    # save manufacturers to CSV
    save_path = MANUFACTURER_SAVE_PATH.joinpath(f"{omniclass.number} {omniclass.name}.csv")
    with open(save_path, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['company name', 'url'])
        for manufacturer in manufacturers:
            writer.writerow([manufacturer.title, manufacturer.url])


async def manufacturer_search_runtime(omniclasses: list[OmniClass], llm: ChatOpenAI):
    """ Find all manufacturers and save the data to a CSV file.

    Parameters:
        `omniclasses`: The list of omniclasses to search for.
        `llm`: The LLM instance to use for checking search results.
    """
    handler = SearchHandler(llm)

    batch_size = 5
    for i in range(0, len(omniclasses), batch_size):
        batch = omniclasses[i:i + batch_size]
        tasks = []
        for omniclass in batch:
            tasks.append(_search_for_manufacturers(omniclass, handler))
        await asyncio.gather(*tasks)
