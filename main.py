#!/usr/bin/python3

from asyncio import run
from pathlib import Path

from db_builders.omniclass.runtime import generate_omniclass_tables, OMNICLASS_SAVE_PATH
from db_builders.loading import parse_remaining
from db_builders.search.runtime import manufacturer_search_runtime, MANUFACTURER_SAVE_PATH
from db_builders.utils import print_bar

REMAINING_FN = Path('remaining.csv')

VALID_MODES = ['1', '2']


# escape codes
LIGHT_BLUE = '\033[94m'
RED = '\033[31m'
LIGHT_GRAY = '\033[37m'
RESET = '\033[0m'
CLEAR = '\033c'


def get_mode() -> str:
    """ Get the mode from the user. """
    while True:
        print(f"Please select a mode: {LIGHT_GRAY}(Input a number to select){RESET}")
        print("1. Generate omniclass tables")
        print("2. Search for manufacturers")
        print("0. Exit")
        print()

        mode = input("Mode: ")
        mode = mode.strip()

        if mode == '0':
            print("Exiting...")
            exit(0)
        elif mode in VALID_MODES:
            return mode
        else:
            print(f"\n{RED}Invalid mode. Please try again.{RESET}\n")


def create_data_directory(path: Path):
    """ Create the data directory if it does not exist. """
    if not path.is_dir():
        path.mkdir()
        print(f"Created directory: {path}")


if __name__ == '__main__':
    # clear terminal window
    print(CLEAR)

    # parse the remaining products
    try:
        OMNICLASS_LIST = parse_remaining(REMAINING_FN)
    except FileNotFoundError:
        print(f"Could not find file: {LIGHT_BLUE}{REMAINING_FN}{RESET}")
        exit(1)

    # select mode
    print_bar("== Select Mode ==")
    print(f"{len(OMNICLASS_LIST)} omniclasses have been loaded.\n")

    current_mode = get_mode()

    # generate omniclass tables
    if current_mode == '1':
        print(CLEAR)

        print_bar("== Generating Omniclass Tables ==")
        print(f"Omniclass tables will be saved to: {LIGHT_BLUE}{OMNICLASS_SAVE_PATH}{RESET}")
        print("This process may take a while...")
        print(f"{RED}Press Ctrl+C to cancel at any time.{RESET}\n")

        # create the data directory if it does not exist
        create_data_directory(OMNICLASS_SAVE_PATH)

        run(generate_omniclass_tables(OMNICLASS_LIST))

    # search for manufacturers
    elif current_mode == '2':
        print(CLEAR)

        print_bar("== Searching for Manufacturers ==")
        print(f"Manufacturer data will be saved to: {LIGHT_BLUE}{MANUFACTURER_SAVE_PATH}{RESET}")
        print("This process may take a while...")
        print(f"{RED}Press Ctrl+C to cancel at any time.{RESET}\n")

        # create the data directory if it does not exist
        create_data_directory(MANUFACTURER_SAVE_PATH)

        run(manufacturer_search_runtime(OMNICLASS_LIST))
