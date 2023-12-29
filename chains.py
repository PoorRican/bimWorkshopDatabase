from langchain.output_parsers import PydanticOutputParser
from langchain_community.chat_models import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import Runnable


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

These 20 values should be pertinent to {product} in the context of architecture and construction.

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
