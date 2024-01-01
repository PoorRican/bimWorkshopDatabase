import csv
from pathlib import Path
from typing import List, Dict

from langchain.pydantic_v1 import BaseModel
from langchain.output_parsers.pydantic import PydanticOutputParser
from langchain_community.chat_models import ChatOpenAI

from dotenv import load_dotenv

from chains import build_parameter_chain, build_parameter_value_chain
from loading import _parse_remaining_omniclass_csv

load_dotenv()


class ParameterList(BaseModel):
    """ This is used to accept a parsed list of parameters from the chatbot."""
    parameters: list[str]


class ValueList(BaseModel):
    """ A list of values for a given BIM parameter """
    values: list[str]


PARAMETER_PARSER = PydanticOutputParser(pydantic_object=ParameterList)
VALUE_PARSER = PydanticOutputParser(pydantic_object=ValueList)


def process_product(product_name: str, chat: ChatOpenAI) -> Dict[str, List[str]]:
    """ Generate a list of parameters and values for a given product name.

    A call to `sleep()` is internally made to avoid OpenAI's rate limits.

    Parameters
    ----------
    product_name : str
        The name of the product to generate parameters and values for.
    chat : ChatOpenAI
        The chatbot to use to generate parameters and values.

    Returns
    -------
    Dict[str, List[str]]
        A dictionary of parameter names to lists of values.
    """
    # generate parameters
    parameter_chain = build_parameter_chain(chat, output_parser=PARAMETER_PARSER)

    parameters = parameter_chain.invoke({"product": product_name})

    # generate values for each parameter
    value_chain = build_parameter_value_chain(chat, output_parser=VALUE_PARSER)
    kv_columns = {}
    for parameter in parameters.parameters:
        values = value_chain.invoke({"parameter": parameter, "product": product_name})
        kv_columns[parameter] = values.values

    return kv_columns


def save_product(path: Path, product_name: str, kv_columns: Dict[str, List[str]]) -> None:
    """ Save a product's parameters and values to a CSV file.

    Parameters
    ----------
    path : Path
        The path to save the final CSV file to.
    product_name : str
        The name of the product to save. Used as the filename.
    kv_columns : Dict[str, List[str]]
        A dictionary of parameter names to lists of values.

    Returns
    -------
    None
    """
    fn = f'{product_name}.csv'
    fn_path = path.joinpath(fn)

    with open(fn_path, 'w') as f:
        writer = csv.writer(f)
        writer.writerow([i for i in kv_columns.keys()])

        # write values
        for i in range(len(kv_columns.keys())):
            writer.writerow([kv_columns[k][i] for k in kv_columns.keys()])


if __name__ == '__main__':
    remaining_fn = Path('remaining_omniclass.csv')

    products = _parse_remaining_omniclass_csv(remaining_fn)

    llm = ChatOpenAI(model_name='gpt-3.5-turbo')
    save_path = Path('data')

    for product in products[:1]:
        print(f"Processing {product}")

        data = process_product(product, llm)
        save_product(save_path, product, data)
