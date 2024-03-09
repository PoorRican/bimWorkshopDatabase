import csv
from pathlib import Path

from db_builders.typedefs import OmniClass


def parse_remaining(path: Path) -> list[OmniClass]:
    """ Parse the "remaining_omniclass.csv" file.

    Parameters
    ----------
    path : Path
        The path to the CSV file.

    Returns
    -------
    None
    """
    # read both columns from the CSV file
    if not path.is_file():
        raise FileNotFoundError(f"Could not find file: {path}")

    omniclass_names = []
    with open(path, 'r') as f:
        reader = csv.reader(f)

        for row in reader:
            omniclass = OmniClass(number=row[0], name=row[1])
            omniclass_names.append(omniclass)

    return omniclass_names


def _load_completed(path: Path) -> set[str]:
    """ Load the set of completed omniclasses from the given file.

    Parameters
    ----------
    path : Path
        The path to the file containing the completed products.

    Returns
    -------
    set[str]
        The set of completed products.
    """
    if not path.is_file():
        raise FileNotFoundError(f"Could not find file: {path}")

    completed = set()
    with open(path, 'r') as f:
        reader = csv.reader(f)

        for row in reader:
            completed.add(row[0])

    return completed


def add_to_completed(path: Path, product_name: str) -> None:
    """ Add a product to the completed set to track which omniclasses have been generated.

    This is called once a CSV file has been generated for a product.

    Parameters
    ----------
    path : Path
        The path to the file containing the completed products.
    product_name : str
        The name of the product to add.

    Returns
    -------
    None
    """
    if not path.is_file():
        raise FileNotFoundError(f"Could not find file: {path}")

    with open(path, 'a') as f:
        writer = csv.writer(f)
        writer.writerow([product_name])


def _extract_remaining(completed: set[str], all_products: list[str]) -> list[str]:
    """ Extract the remaining omniclasses from the set of completed omniclasses.

    This is called at the beginning of runtime to get a list of omniclasses that still need to be generated.

    Parameters
    ----------
    completed : set[str]
        The set of completed products.
    all_products : list[str]
        The list of all products.

    Returns
    -------
    list[str]
        The list of remaining products.
    """
    return [p for p in all_products if p not in completed]


def get_remaining(remaining_path: Path, completed_path: Path) -> list[str]:
    """ Get the list of remaining omniclasses.

    This function is exposed and expected to be called by the main script.

    Parameters
    ----------
    remaining_path : Path
        The path to the file containing the remaining omniclasses.
    completed_path : Path
        The path to the file containing the completed omniclasses.

    Returns
    -------
    list[str]
        The list of remaining omniclasses.
    """
    remaining = parse_remaining(remaining_path)
    completed = _load_completed(completed_path)

    return _extract_remaining(completed, remaining)
