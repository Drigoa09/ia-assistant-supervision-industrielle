from typing import Literal
from OrderState import OrderState

from model import model_mistral_medium

def continuer_node(state: OrderState) -> OrderState:
    """The chatbot itself. A wrapper around the model's own chat interface."""

    state['i'] += 1
    
    if state['i'] < len(state['traitements']):
        state['traitement'] = state['traitements'][state['i']]
    else:
        request = model_mistral_medium.invoke("Fait apparaître une chanson de Jul au hasard avec les paroles")
        return state | {'messages' : request}

    return state

def maybe_route_to_treatment(state: OrderState) -> Literal["Formulateur de requêtes de traitement", "Humain"]:
    """Route to the chatbot, unless it looks like the user is exiting."""

    # When the chatbot returns tool_calls, route to the "tools" node.
    if state['i'] < len(state['traitements']):
        return "Formulateur de requêtes de traitement"
    else:
        return "Humain"
