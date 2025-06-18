from typing import Literal
from OrderState import OrderState

def continuer_node(state: OrderState) -> OrderState:
    """The chatbot itself. A wrapper around the model's own chat interface."""

    state['i'] += 1
    
    if state['i'] < len(state['traitements']):
        state['traitement'] = state['traitements'][state['i']]

    return state

def maybe_route_to_treatment(state: OrderState) -> Literal["treatment_agent", "human"]:
    """Route to the chatbot, unless it looks like the user is exiting."""

    # When the chatbot returns tool_calls, route to the "tools" node.
    if state['i'] < len(state['traitements']):
        return "treatment_agent"
    else:
        return "human"
