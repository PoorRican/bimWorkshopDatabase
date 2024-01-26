from asyncio import sleep, gather
from pathlib import Path

from db_builders.omniclass import generate_parameters, generate_all_values, save_product
from db_builders.typedefs import OmniClass
from main import OMNICLASS_LIST, CHUNK_SIZE


OMNICLASS_SAVE_PATH = Path('data/omniclass_tables')


async def _process_product(omniclass: OmniClass):
    omniclass_name = omniclass.name
    print(f"\n*** Processing {omniclass_name}...")
    ai_message, parameters = await generate_parameters(omniclass_name)
    kv_columns = await generate_all_values(omniclass_name, parameters, ai_message)
    save_product(OMNICLASS_SAVE_PATH, omniclass, kv_columns)
    print(f"\n*** ...Done processing {omniclass_name}. ***\n")


async def generate_omniclass_tables(omniclasses: list[OmniClass]):
    # give some feedback on how many products are being processed
    print(f"Processing {len(OMNICLASS_LIST)} products...")

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
