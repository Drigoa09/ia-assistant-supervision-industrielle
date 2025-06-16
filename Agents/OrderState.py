from typing import Annotated, TypedDict
from langgraph.graph.message import add_messages

from Tools_nodes.database_tools.request_format import request 

class OrderState(TypedDict):
    """State representing the customer's order conversation."""

    # The chat conversation. This preserves the conversation history
    # between nodes. The `add_messages` annotation indicates to LangGraph
    # that state is updated by appending returned messages, not replacing
    # them.
    messages: Annotated[list, add_messages]

    request_call : Annotated[request, 'Contient les requêtes']

    # The customer's in-progress order.
    order: list[str]

    question:list
    tools_to_answer: list


    # Flag indicating that the order is placed and completed.
    finished: bool
    Trois : bool
