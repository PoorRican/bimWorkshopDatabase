from operator import itemgetter

from langchain.output_parsers import PydanticOutputParser
from langchain_community.chat_models import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import Runnable


def extract_list_from_response(response: str) -> list[str]:
    """ Extract a list of values from the response.

    Parameters
    ----------
    response: str
        The response to extract values from.

    Returns
    -------
    list[str]
        The list of values.
    """
    # remove any text after "]"
    response = response.split("]")[0]

    if response[0] != "[":
        response = "[" + response

    if response[-1] != "]":
        response = response + "]"

    extracted: list[str] = eval(response)
    return extracted


def build_explanation_chain(chat: ChatOpenAI) -> Runnable:
    """ Build a chain of runnables to generate an explanation for a given product.

    The runnable accepts a dictionary with the following key:
    - product: The label of the product to generate an explanation for.

    The output of the runnable is a parsed `str` object.

    Parameters
    ----------
    chat : ChatOpenAI
        The chatbot to use to generate an explanation.

    Returns
    -------
    Runnable
        The chain of runnables to generate an explanation.
    """
    explanatory_prompt = PromptTemplate.from_template(
        """I will give you $30,000 which you can donate to the charity of your choice if your answer contains sufficient information that me, as an engineer, do not already know.

I am an architect and engineer looking to learn more about the detail of a given product. We are currently in the design phase, and I want to know if there are attributes about a certain product of which I forgot about or am not aware of when specifying the requirements during the design phase.

The goal is to provide an explanation of the non-obvious factors that I need to consider when selecting a product. I am looking to add data to an OmniClass table to use for specification purposes to send to a contractor.

Please give me 20 parameters for {product}"""
    )

    explanatory_chain = explanatory_prompt | chat | StrOutputParser()
    return explanatory_chain


def build_parameter_chain(chat: ChatOpenAI) -> Runnable:
    """ Build a chain of runnables to generate a list of parameters for a given product.

    The runnable accepts a dictionary with the following key:
    - product: The label of the product to generate parameters for.

    The output of the runnable is a parsed `ParameterList` object.

    Parameters
    ----------
    chat : ChatOpenAI
        The chatbot to use to generate parameters.

    Returns
    -------
    Runnable
    """
    # layer for explaining the product
    # layer to extract parameters
    parameter_prompt = PromptTemplate.from_template(
        """I'm an engineer looking to understand the specific parameters I need to account for when selecting a product in an architectural design when specifying the requirements during the design phase.
        
Here is an explanation of the product:
"{explanation}"
        
Please give me a python list of the most important or non-obvious parameters I need to consider during the design phase when specifying the requirements.
        
```python
[
""")

    return (
        {'explanation': itemgetter('explanation')}
        | parameter_prompt
        | chat | StrOutputParser()
    )


def build_parameter_value_chain(chat: ChatOpenAI, parse_chat: ChatOpenAI) -> Runnable:
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

These 20 values should be pertinent to {product} in the context of architecture and construction.

Only return the values, not the parameter names or their descriptions.""")

    chain = (
        prompt
        | chat
        | StrOutputParser()
    )

    formatter_prompt = PromptTemplate.from_template(
        """Please format the given list as a valid python list:

For example:
1. foo
2. bar

becomes:
```python
["foo", "bar"]
```

Here is the list of values:
{values}

```python
[
""")

    return (
        {'values': chain}
        | formatter_prompt
        | parse_chat
        | StrOutputParser()
    )
