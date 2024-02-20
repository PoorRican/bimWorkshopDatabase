#!/usr/bin/python3
import os
from asyncio import run
from pathlib import Path

from db_builders.name_finder.parsing import parse_name_file
from db_builders.name_finder.runtime import MANUFACTURER_NAME_FILE, product_page_search_runtime
from db_builders.omniclass.runtime import generate_omniclass_tables, OMNICLASS_SAVE_PATH
from db_builders.loading import parse_remaining
from db_builders.search.runtime import manufacturer_search_runtime, MANUFACTURER_SAVE_PATH
from db_builders.utils import print_bar

DATA_DIR = Path('data')
REMAINING_FN = Path('remaining.csv')

VALID_MODES = ['1', '2', '3']


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
        print("3. Get product pages")
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


if __name__ == '__main__':
    # create data directory
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # clear terminal window
    print(CLEAR)

    print_bar("== Select Mode ==")
    print()

    # try to parse the remaining products
    try:
        OMNICLASS_LIST = parse_remaining(REMAINING_FN)
        print(f"{LIGHT_BLUE}{len(OMNICLASS_LIST)} omniclasses{RESET} have been loaded.")
    except FileNotFoundError:
        print(f"Could not find file: {LIGHT_BLUE}{REMAINING_FN}{RESET}")
        OMNICLASS_LIST = None

    # try to parse manufacturer names
    try:
        MANUFACTURER_NAMES = parse_name_file(MANUFACTURER_NAME_FILE)
        print(f"{LIGHT_BLUE}{len(MANUFACTURER_NAMES)} manufacturer names{RESET} have been loaded.")
    except FileNotFoundError:
        print(f"Could not find file: {LIGHT_BLUE}{MANUFACTURER_NAME_FILE}{RESET}")
        MANUFACTURER_NAMES = None

    # select mode
    print()
    current_mode = get_mode()

    # generate omniclass tables
    if current_mode == '1':
        if OMNICLASS_LIST is None:
            print(f"{RED}No omniclass data found. Exiting...{RESET}")
            exit(1)
        print(CLEAR)

        print_bar("== Generating Omniclass Tables ==")
        print(f"Omniclass tables will be saved to: {LIGHT_BLUE}{OMNICLASS_SAVE_PATH}{RESET}")
        print("This process may take a while...")
        print(f"{RED}Press Ctrl+C to cancel at any time.{RESET}\n")

        run(generate_omniclass_tables(OMNICLASS_LIST))

    # search for manufacturers
    elif current_mode == '2':
        if OMNICLASS_LIST is None:
            print(f"{RED}No omniclass data found. Exiting...{RESET}")
            exit(1)
        print(CLEAR)

        print_bar("== Searching for Manufacturers ==")
        print(f"Manufacturer data will be saved to: {LIGHT_BLUE}{MANUFACTURER_SAVE_PATH}{RESET}")
        print("This process may take a while...")
        print(f"{RED}Press Ctrl+C to cancel at any time.{RESET}\n")

        run(manufacturer_search_runtime(OMNICLASS_LIST))

    elif current_mode == '3':
        if MANUFACTURER_NAMES is None:
            print(f"{RED}No manufacturer names found. Exiting...{RESET}")
            exit(1)
        print(CLEAR)

        print_bar("== Getting Product Pages ==")
        print(f"Manufacturer data will be loaded from: {LIGHT_BLUE}{MANUFACTURER_NAME_FILE}{RESET}")
        print("This process may take a while...")
        print(f"{RED}Press Ctrl+C to cancel at any time.{RESET}\n")

        run(product_page_search_runtime(MANUFACTURER_NAMES))
