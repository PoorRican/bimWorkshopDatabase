#!/usr/bin/python3

from asyncio import run
from pathlib import Path

from db_builders.omniclass.runtime import generate_omniclass_tables, OMNICLASS_SAVE_PATH
from db_builders.loading import parse_remaining

CHUNK_SIZE = 3
REMAINING_FN = Path('remaining.csv')


def create_data_directory():
    """ Create the data directory if it does not exist. """
    if not OMNICLASS_SAVE_PATH.is_dir():
        OMNICLASS_SAVE_PATH.mkdir()
        print(f"Created directory: {OMNICLASS_SAVE_PATH}")


if __name__ == '__main__':
    # clear terminal window
    print('\033c')

    # create the data directory if it does not exist
    create_data_directory()

    # parse the remaining products
    try:
        OMNICLASS_LIST = parse_remaining(REMAINING_FN)

        run(generate_omniclass_tables(OMNICLASS_LIST))
    except FileNotFoundError:
        print(f"Could not find file: {REMAINING_FN}")
        exit(1)
