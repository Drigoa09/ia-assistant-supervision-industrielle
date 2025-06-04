from langchain_core.messages.ai import AIMessage
from OrderState import OrderState
from typing import Literal
from model import model

AGENT_GENERATION_SYSINT = (
    "Your goal is to answer questions"
)

WELCOME_MSG = (
    "Hi boi, how can i help u ?"
)

def chatbot_with_welcome_msg(state: OrderState) -> OrderState:
    """The chatbot itself. A wrapper around the model's own chat interface."""

    if state["messages"]:
        # If there are messages, continue the conversation with the Mistral model.
        new_output = model.invoke([AGENT_GENERATION_SYSINT] + state["messages"])
    else:
        # If there are no messages, start with the welcome message.
        new_output = AIMessage(content=WELCOME_MSG)

    return state | {"messages": [new_output]}

def maybe_route_to_database(state: OrderState) -> Literal["chatbot", "__end__"]:
    """Route to the chatbot, unless it looks like the user is exiting."""
    if state.get("finished", False):
        return END
    else:
        return "chatbot"