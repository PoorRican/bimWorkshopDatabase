#!/usr/bin/python3

from asyncio import sleep, gather, run
from pathlib import Path

from src.db_builder import process_product, SAVE_PATH
from src.loading import OmniClass, parse_remaining

CHUNK_SIZE = 3
REMAINING_FN = Path('remaining.csv')


async def run_all(omniclasses: list[OmniClass]):
    # give some feedback on how many products are being processed
    print(f"Processing {len(OMNICLASS_LIST)} products...")

    # wait 5 seconds before starting
    print("Processing will start in 5 seconds... (press Ctrl+C to cancel at any time)")
    await sleep(5)

    # chunk products into groups of CHUNK_SIZE
    chunks = [omniclasses[i:i + CHUNK_SIZE] for i in range(0, len(omniclasses), CHUNK_SIZE)]
    for chunk in chunks:
        tasks = [process_product(product_name) for product_name in chunk]
        await gather(*tasks)

    # print the number of products that were processed
    print(f"\nProcessed {len(omniclasses)} products.")
    print("Done!")
    exit(0)


def create_data_directory():
    """ Create the data directory if it does not exist. """
    if not SAVE_PATH.is_dir():
        SAVE_PATH.mkdir()
        print(f"Created directory: {SAVE_PATH}")


if __name__ == '__main__':
    # clear terminal window
    print('\033c')

    # create the data directory if it does not exist
    create_data_directory()

    # parse the remaining products
    try:
        OMNICLASS_LIST = parse_remaining(REMAINING_FN)

        run(run_all(OMNICLASS_LIST))
    except FileNotFoundError:
        print(f"Could not find file: {REMAINING_FN}")
        exit(1)
