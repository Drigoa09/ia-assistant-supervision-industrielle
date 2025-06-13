from typing import Literal
from langchain_core.messages import AIMessage, HumanMessage
from OrderState import OrderState
from model import model

WELCOME_MSG = (
    "Bonjour ! Je suis votre assistant, comment puis-je vous aider?"
)

AGENT_GENERATION_SYSINT = (
    '''Génère une réponse à partir du message qu'on te donne.'''
)

def generer_reponse(state: OrderState) -> OrderState:
    """The chatbot itself. A wrapper around the model's own chat interface."""

    # If there are messages, continue the conversation with the Mistral model.
    if state["messages"]:

        new_output = model.invoke(state["messages"] + [HumanMessage(AGENT_GENERATION_SYSINT)])

    else:

        new_output = AIMessage(content=WELCOME_MSG)
    return state | {"messages": [new_output]}
