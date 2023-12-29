import csv
from pathlib import Path


def parse_remaining_omniclass_csv(path: Path) -> list[str]:
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
            omniclass_names.append(' '.join(row))

    return omniclass_names
