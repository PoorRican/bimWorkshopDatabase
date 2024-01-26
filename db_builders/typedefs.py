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

    def __str__(self):
        return f"{self.number} {self.name}"


@dataclass
class SearchResultItem:
    """ This is used to parse the results from the Google custom search API """
    title: str
    link: str
    snippet: str
