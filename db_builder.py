import asyncio
import csv
from pathlib import Path
from typing import List, Dict

from langchain_community.chat_models import ChatOpenAI

from dotenv import load_dotenv

from chains import build_parameter_chain, build_parameter_value_chain, extract_list_from_response, \
    build_explanation_chain
from loading import _parse_remaining_omniclass_csv

load_dotenv()

SAVE_PATH = Path('data')

GPT4 = ChatOpenAI(model_name='gpt-4')
GPT3 = ChatOpenAI(model_name='gpt-3.5-turbo')


EXPLANATION_CHAIN = build_explanation_chain(GPT4)
PARAMETER_CHAIN = build_parameter_chain(GPT3)
VALUE_CHAIN = build_parameter_value_chain(GPT4, GPT3)


async def generate_parameters(product_name: str) -> list[str]:
    explanation = await EXPLANATION_CHAIN.ainvoke({"product": product_name})
    llm_response = await PARAMETER_CHAIN.ainvoke({"product": product_name, "explanation": explanation})
    return extract_list_from_response(llm_response)


async def generate_all_values(product_name: str, parameters: list[str]) -> Dict[str, List[str]]:
    kv_columns = {}

    tasks = [generate_values(product_name, parameter) for parameter in parameters]

    for parameter, values in zip(parameters, await asyncio.gather(*tasks)):
        kv_columns[parameter] = values

    return kv_columns


async def generate_values(product_name: str, parameter: str) -> list[str]:
    value_response = await VALUE_CHAIN.ainvoke({
        "parameter": parameter,
        "product": product_name})
    return extract_list_from_response(value_response)


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
    parameters = await generate_parameters(product_name)
    kv_columns = await generate_all_values(product_name, parameters)
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
