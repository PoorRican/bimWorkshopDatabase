import asyncio
import csv
from pathlib import Path

from db_builders.llm import GPT3_LOW_T
from db_builders.name_finder.finder import WebsiteFinder
from db_builders.name_finder.parsing import parse_name_file

MANUFACTURER_NAME_FILE = 'manufacturer_names.csv'
MANUFACTURER_URLS_SAVE_PATH = Path('data/manufacturer_product_pages.csv')

# TODO: if performance is bad, get manufacturer url, then perform another search using the site


def _save_manufacturer_urls(urls: dict[str, str], save_path: Path):
    """ Save the manufacturer URLs to a CSV file.
    """
    with open(save_path, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['manufacturer name', 'product page'])

        for name, url in urls.items():
            writer.writerow([name, url])


async def _get_manufacturer_urls(file_path: str) -> dict[str, str]:
    """ Get the manufacturer URLs for the given manufacturer names
    """
    names = parse_name_file(file_path)

    batch = 10
    urls = {}

    async with WebsiteFinder(GPT3_LOW_T) as finder:
        for i in range(0, len(names), batch):
            print(f"Getting URLs for names {i} to {i + batch}...")
            names_batch = names[i:i + batch]
            tasks = [finder(name) for name in names_batch]
            results = await asyncio.gather(*tasks)
            urls.update({name: result for name, result in zip(names_batch, results)})

    return urls


async def product_page_search_runtime():
    """ Perform the search for manufacturer product pages.
    """
    urls = await _get_manufacturer_urls(MANUFACTURER_NAME_FILE)
    _save_manufacturer_urls(urls, MANUFACTURER_URLS_SAVE_PATH)
