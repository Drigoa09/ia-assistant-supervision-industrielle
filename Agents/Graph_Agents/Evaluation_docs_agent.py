from langchain_core.messages.ai import AIMessage
from OrderState import OrderState
from model import model

AGENT_GENERATION_SYSINT = (
    '''
    Donne un score entre 1 et 5 sur la pertinence des documents que tu as reçu ?
'''
)

def evaluation_docs_agent(state: OrderState) -> OrderState:
    """The chatbot itself. A wrapper around the model's own chat interface."""

    # If there are messages, continue the conversation with the Mistral model.

    new_output = model.invoke([AGENT_GENERATION_SYSINT] + [state["messages"][-2].content])

    return state | {"messages": [new_output]}