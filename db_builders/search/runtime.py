import asyncio
import csv
from pathlib import Path

from db_builders.llm import GPT3_LOW_T
from db_builders.search.search_handler import SearchHandler
from db_builders.typedefs import Manufacturer, OmniClass


MANUFACTURER_SAVE_PATH = Path('data/manufacturers')


async def _search_for_manufacturers(omniclass: OmniClass,
                                    handler: SearchHandler,
                                    num_results: int = 1000):
    """ Search for manufacturers for a given omniclass.

    This is used as a coroutine in `manufacturer_search_runtime` to execute in parallel.

    Parameters:
        `omniclass`: The omniclass to search for.
        `handler`: The `SearchHandler` to use for searching.
        `num_results`: The number of results to search for. Defaults to 1000.
    """
    print(f"Getting manufacturers for {omniclass.number} {omniclass.name}")
    results = await handler(omniclass.name, num_results)
    _save_manufacturers(omniclass, results)


def _save_manufacturers(omniclass: OmniClass, manufacturers: list[Manufacturer]):
    """ Save manufacturers to a CSV file.

    The CSV file will be saved in the `data/manufacturers` directory and named appropriately
    based on the `omniclass` parameter.

    Parameters:
        `omniclass`: The omniclass to save manufacturers for.
        `manufacturers`: The list of manufacturers to save.
    """
    # save manufacturers to CSV
    save_path = MANUFACTURER_SAVE_PATH.joinpath(f"{omniclass.number} {omniclass.name}.csv")
    with open(save_path, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['company name', 'url'])
        for manufacturer in manufacturers:
            writer.writerow([manufacturer.title, manufacturer.url])


async def manufacturer_search_runtime(omniclasses: list[OmniClass]):
    """ Find all manufacturers and save the data to a CSV file.

    This is the main entry point for the manufacturer search runtime and should be the only function
    called in `main.py`.

    Parameters:
        `omniclasses`: The list of omniclasses to search for.
        `llm`: The LLM instance to use for checking search results.
    """
    handler = SearchHandler(GPT3_LOW_T)

    batch_size = 5
    for i in range(0, len(omniclasses), batch_size):
        batch = omniclasses[i:i + batch_size]
        tasks = []
        for omniclass in batch:
            tasks.append(_search_for_manufacturers(omniclass, handler))
        await asyncio.gather(*tasks)
