import asyncio
import csv
from pathlib import Path
from typing import List, Dict

from langchain_community.chat_models import ChatOpenAI

from dotenv import load_dotenv
from langchain_core.messages import AIMessage

from chains import build_parameter_chain, build_parameter_value_chain, extract_list_from_response, build_formatter_chain
from loading import _parse_remaining_omniclass_csv

load_dotenv()

SAVE_PATH = Path('data')

GPT3_LOW_T = ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0.3)
GPT3_HIGH_T = ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0.9)


PARAMETER_CHAIN = build_parameter_chain(GPT3_HIGH_T)
VALUE_CHAIN = build_parameter_value_chain(GPT3_LOW_T, GPT3_LOW_T)
FORMATTER_CHAIN = build_formatter_chain(GPT3_LOW_T)


async def _generate_parameters(product_name: str) -> (AIMessage, list[str]):
    llm_response = await PARAMETER_CHAIN.ainvoke({"omniclass": product_name})
    formatted = await FORMATTER_CHAIN.ainvoke({"content": llm_response.content})
    parameter_list = extract_list_from_response(formatted)
    return llm_response, parameter_list


async def generate_parameters(product_name: str) -> (AIMessage, list[str]):
    while True:
        ai_message, parameters = await _generate_parameters(product_name)
        if len(parameters) == 20:
            return ai_message, parameters
        else:
            print("Got less than 20 parameters, retrying...")


async def generate_all_values(product_name: str, parameters: list[str], ai_message: AIMessage) -> Dict[str, List[str]]:
    assert len(parameters) == 20

    ordinals = [
        "first",
        "2nd",
        "3rd",
        "4th",
        "5th",
        "6th",
        "7th",
        "8th",
        "9th",
        "10th",
        "11th",
        "12th",
        "13th",
        "14th",
        "15th",
        "16th",
        "17th",
        "18th",
        "19th",
        "twentieth"
    ]
    kv_columns = {}

    tasks = [generate_values(product_name, ordinal, ai_message) for ordinal in ordinals]

    for parameter, values in zip(parameters, await asyncio.gather(*tasks)):
        kv_columns[parameter] = values

    return kv_columns


async def _generate_values(product_name: str, ordinal: str, ai_message: AIMessage) -> list[str]:
    value_response = await VALUE_CHAIN.ainvoke({
        "ordinal": ordinal,
        "ai_message": [ai_message],
        "omniclass": product_name})
    return extract_list_from_response(value_response)


async def generate_values(product_name: str, ordinal: str, ai_message: AIMessage) -> list[str]:
    while True:
        values = await _generate_values(product_name, ordinal, ai_message)
        if len(values) == 20:
            return values
        else:
            print("Got less than 20 values, retrying...")


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


async def process_product(product_name: str):
    ai_message, parameters = await generate_parameters(product_name)
    kv_columns = await generate_all_values(product_name, parameters, ai_message)
    save_product(SAVE_PATH, product_name, kv_columns)


async def run_all(products: list[str]):
    # tasks = [process_product(product) for product in products]
    # await asyncio.gather(*tasks)
    for product in products:
        print(f'Processing {product}')
        await process_product(product)


if __name__ == '__main__':
    remaining_fn = Path('remaining_omniclass.csv')

    # products = _parse_remaining_omniclass_csv(remaining_fn)
    PRODUCTS = [
        'Roof Coverings',
        'Porcelain Glazing Laboratory Furnaces',
        'Vacuum Porcelain Furnaces',
        'Audio Security Sensors'
    ]

    asyncio.run(run_all(PRODUCTS))
