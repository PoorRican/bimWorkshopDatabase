import re

from pydantic import BaseModel


class Omniclass(BaseModel):
    """ A class to represent an Omniclass product.

    This is used to store the name of the product and the name of the CSV file that was generated for it.
    """
    number: str
    name: str

    def __str__(self):
        return f"{self.number} {self.name}"

    @property
    def identifier(self) -> str:
        """ Return the identifier for the omniclass.

        This is used to generate the filename for the CSV file.
        """
        return str(self)

    @staticmethod
    def parse_identifier(identifier: str) -> tuple[str, str]:
        """ Parse an Omniclass identifier into the omniclass number and name.

        Parameters:
            identifier (str): The identifier to parse.

        Returns:
            A tuple of the omniclass number and name.
        """
        regex_pattern = r"(?P<number>(\d{2}-\d{2}(\s\d{2})*)+) (?P<name>.*)"
        match = re.match(regex_pattern, identifier)
        if not match:
            raise ValueError(f"Could not parse filename: {identifier}")
        else:
            return match.group('number'), match.group('name')
