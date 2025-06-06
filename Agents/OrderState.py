from typing import Annotated, TypedDict
from langgraph.graph.message import add_messages

class OrderState(TypedDict):
    """State representing the customer's order conversation."""

    # The chat conversation. This preserves the conversation history
    # between nodes. The `add_messages` annotation indicates to LangGraph
    # that state is updated by appending returned messages, not replacing
    # them.
    messages: Annotated[list, add_messages]

    # The customer's in-progress order.
    order: list[str]

    question:list
    tools_to_answer: list

    # Flag indicating that the order is placed and completed.
    finished: bool

    def getQuestion(self) -> list:
        return self.question
    
    def get_tools_to_answer(self) -> list:
        return self.tools_to_answer

    def setQuestion(self, question:list) -> None:
        self.question = question

    def reset_tools_to_answer(self) -> None:
        self.tools_to_answer = []

    def add_element_in_tools_to_answer(self, element) -> None:
        self.tools_to_answer.append(element)
