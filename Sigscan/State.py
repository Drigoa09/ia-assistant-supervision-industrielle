from typing import Annotated, List, TypedDict
from langgraph.graph.message import add_messages

class State(TypedDict):

    messages : Annotated[List, add_messages] = []

    question : str = ""

    call_request : dict = {}

    finished : bool = False

    dataFrames: list
