import csv
from pathlib import Path
from typing import List, Dict

from langchain.output_parsers import RetryWithErrorOutputParser
from langchain.prompts import PromptTemplate
from langchain.pydantic_v1 import BaseModel
from langchain.output_parsers.pydantic import PydanticOutputParser
from langchain_community.chat_models import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import Runnable

from dotenv import load_dotenv

load_dotenv()


class ParameterList(BaseModel):
    """ This is used to accept a parsed list of parameters from the chatbot."""
    parameters: list[str]


class ValueList(BaseModel):
    """ A list of values for a given BIM parameter """
    values: list[str]


PARAMETER_PARSER = PydanticOutputParser(pydantic_object=ParameterList)
VALUE_PARSER = PydanticOutputParser(pydantic_object=ValueList)


def build_parameter_chain(chat: ChatOpenAI, output_parser: PydanticOutputParser) -> Runnable:
    """ Build a chain of runnables to generate a list of parameters for a given product.

    The runnable accepts a dictionary with the following key:
    - product: The label of the product to generate parameters for.

    The output of the runnable is a parsed `ParameterList` object.

    Parameters
    ----------
    chat : ChatOpenAI
        The chatbot to use to generate parameters.
    output_parser : PydanticOutputParser
        The output parser to use to parse the parameters.

    Returns
    -------
    Runnable
    """
    prompt = PromptTemplate.from_template(
        """I am an architect and want to describe building products in detail.
        
I am looking to create a list of 20 accurate BIM Parameters for an omniclass.

Exclude manufacturer specific parameters such as manufacturer, serial number, model name, etc.
Exclude parameters such as dimensions, weight, height, cost, etc.

These parameters should be pertinent to architecture and construction.

Return a list of 20 parameters that are relevant to the {product} omniclass as a list of strings.

Only return the parameter names, not the values or their descriptions.""")

    formatter_prompt = PromptTemplate.from_template(
        """Format the following:
        
{parameters}

{format_instructions}""",
        partial_variables={'format_instructions': output_parser.get_format_instructions()}
    )

    chain = prompt | chat | StrOutputParser()

    return (
        {'parameters': chain}
        | formatter_prompt
        | chat
        | output_parser
    )


def build_parameter_value_chain(chat: ChatOpenAI, output_parser: PydanticOutputParser) -> Runnable:
    """ Build a chain of runnables to generate a list of values for a given parameter.

    The runnable accepts a dictionary with the following keys:
    - parameter: The name of the parameter to generate values for.
    - product: The label of the product to generate values for.

    The output of the runnable is a parsed `ParameterList` object.

    Parameters
    ----------
    chat : ChatOpenAI
        The chatbot to use to generate values.
    output_parser : PydanticOutputParser
        The output parser to use to parse the values.

    Returns
    -------
    Runnable
        The chain of runnables to generate values.
    """
    prompt = PromptTemplate.from_template(
        """I am an architect and want to describe building products in detail for use in BIM.

Return a list of 20 values that are relevant to the {parameter} parameter for the omniclass {product}.

These values should be pertinent to architecture and construction.

Only return the values, not the parameter names or their descriptions.""")

    formatter_prompt = PromptTemplate.from_template(
        """ Format the following list of parameter values according to the given schema:
    
{values}
        
{format_instructions}""",
        partial_variables={'format_instructions': output_parser.get_format_instructions()}
    )

    chain = prompt | chat | StrOutputParser()

    return (
        {'values': chain}
        | formatter_prompt
        | chat
        | output_parser
    )


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
        print(f"Values for {parameter}:\n{values}")
        kv_columns[parameter] = values

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
        # write header
        f.write(','.join(kv_columns.keys()) + '\n')

        # write values
        for i in range(len(kv_columns.keys())):
            f.write(','.join([kv_columns[k][i] for k in kv_columns.keys()]) + '\n')


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


if __name__ == '__main__':
    remaining_fn = Path('remaining_omniclass.csv')

    products = parse_remaining_omniclass_csv(remaining_fn)

    llm = ChatOpenAI(model_name='gpt-3.5-turbo')
    save_path = Path('data')

    for product in products[:1]:
        print(f"Processing {product}")

        data = process_product(product, llm)
        for k, v in data.items():
            print(f"{k}: {v}")
