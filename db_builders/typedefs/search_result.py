from pydantic import BaseModel


class SearchResultItem(BaseModel):
    """ This is used to parse the results from the Google custom search API """
    title: str
    link: str
    snippet: str
