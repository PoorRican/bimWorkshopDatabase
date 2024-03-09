from pydantic import BaseModel


class Omniclass(BaseModel):
    """ A class to represent an Omniclass product.

    This is used to store the name of the product and the name of the CSV file that was generated for it.
    """
    number: str
    name: str

    def __str__(self):
        return f"{self.number} {self.name}"
