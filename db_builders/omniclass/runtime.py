from asyncio import sleep, gather
from pathlib import Path

from db_builders.omniclass.builder_functions import generate_parameters, generate_all_values, save_product
from db_builders.typedefs import Omniclass


CHUNK_SIZE = 3
OMNICLASS_SAVE_PATH = Path('data/omniclass_tables')


async def _process_product(omniclass: Omniclass):
    """ Begin to process a single omniclass product.

    This is used as a coroutine in `generate_omniclass_tables` to execute in parallel.

    Data is saved to a CSV file in the `data/omniclass_tables` directory.

    Parameters:
        `omniclass`: A single omniclass to process.
    """
    omniclass_name = omniclass.name
    print(f"\n*** Processing {omniclass_name}...")
    ai_message, parameters = await generate_parameters(omniclass_name)
    kv_columns = await generate_all_values(omniclass_name, parameters, ai_message)
    save_product(OMNICLASS_SAVE_PATH, omniclass, kv_columns)
    print(f"\n*** ...Done processing {omniclass_name}. ***\n")


async def generate_omniclass_tables(omniclasses: list[Omniclass]):
    """ Generate omniclass tables for a given list of omniclass objects.

    This is the main entry point for the omniclass table generation runtime and should be the only function
    called in `main.py`.

    Parameters:
        `omniclasses`: The list of omniclasses to generate tables for
    """
    # create directory if it does not exist
    OMNICLASS_SAVE_PATH.mkdir(parents=True, exist_ok=True)

    # give some feedback on how many products are being processed
    print(f"Processing {len(omniclasses)} products...")

    # wait 5 seconds before starting
    print("Processing will start in 5 seconds... (press Ctrl+C to cancel at any time)")
    await sleep(5)

    # chunk products into groups of CHUNK_SIZE
    chunks = [omniclasses[i:i + CHUNK_SIZE] for i in range(0, len(omniclasses), CHUNK_SIZE)]
    for chunk in chunks:
        tasks = [_process_product(product_name) for product_name in chunk]
        await gather(*tasks)

    # print the number of products that were processed
    print(f"\nProcessed {len(omniclasses)} products.")
    print("Done!")
    exit(0)
