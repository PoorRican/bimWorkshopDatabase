import csv


def parse_name_file(file_path: str) -> list[str]:
    """ Parse the file containing the manufacturer names.

    This function is called by the main script to get the list of manufacturer names.

    Parameters
    ----------
    file_path : str
        The path to the file containing the manufacturer names.

    Returns
    -------
    list[str]
        The list of manufacturer names.
    """
    names = []
    with open(file_path, "r") as f:
        reader = csv.reader(f)

        for row in reader:
            try:
                name = row[0].strip()
                names.append(name)
            except IndexError:
                # skip empty lines
                pass

    return names
