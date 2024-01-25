from dataclasses import dataclass


@dataclass
class Manufacturer:
    title: str
    url: str


@dataclass
class Parameter:
    name: str
    values: list[str]


@dataclass
class OmniClass:
    """ A class to represent an OmniClass product.

    This is used to store the name of the product and the name of the CSV file that was generated for it.
    """
    number: str
    name: str
