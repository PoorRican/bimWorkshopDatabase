import asyncio
import csv
from pathlib import Path
from typing import Tuple

from db_builders.llm import GPT3_LOW_T
from db_builders.name_finder.product_page_finder import ProductPageFinder
from db_builders.name_finder.website_finder import WebsiteFinder
from db_builders.utils import strip_url, print_bar

MANUFACTURER_NAME_FILE = 'manufacturer_names.csv'
MANUFACTURER_URLS_SAVE_PATH = Path('data/manufacturer_product_pages.csv')


def _save_manufacturer_urls(urls: dict[str, Tuple[str, str]], save_path: Path):
    """ Save the manufacturer URLs to a CSV file.
    """
    with open(save_path, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['manufacturer name', 'url', 'product page'])

        for name, urls in urls.items():
            url, product_page = urls
            writer.writerow([name, url, product_page])


async def _find_manufacturer_urls(manufacturer_name: str) -> Tuple[str, str]:
    """ Get the manufacturer URL for the given manufacturer name

    Parameters:
        manufacturer_name: Manufacturer name to search for

    Returns:
        Tuple of website URL and product page URL
    """
    # find manufacturer website
    finder = WebsiteFinder(GPT3_LOW_T)
    base_url = await finder(manufacturer_name)

    base_url = strip_url(base_url)

    # find product page
    finder = ProductPageFinder(GPT3_LOW_T)
    product_page = await finder(manufacturer_name, base_url)

    return base_url, product_page


async def _perform_manufacture_url_search(file_path: str) -> dict[str, Tuple[str, str]]:
    """ Get the manufacturer URLs for the local file.
    """


async def product_page_search_runtime(names: list[str]):
    """ Perform the search for manufacturer product pages and save to disk.

    Results are incrementally saved to disk after each batch of names is processed.

    Parameters:
        names: List of manufacturer names to search for
    """
    batch = 10

    # find manufacturer websites
    urls = {}
    for i in range(0, len(names), batch):

        if i + batch > len(names):
            last = len(names) - i
        else:
            last = i + batch
        print(f"Processing batch {i + 1} - {last} of {len(names)} manufacturer names")

        names_batch = names[i:i + batch]
        tasks = [_find_manufacturer_urls(name) for name in names_batch]
        results = await asyncio.gather(*tasks)

        urls.update({name: result for name, result in zip(names_batch, results)})

        _save_manufacturer_urls(urls, MANUFACTURER_URLS_SAVE_PATH)

    print_bar("== Finished ==")

    print(f"Processed {len(urls)} manufacturer names")
