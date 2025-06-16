from Tools_nodes.database_tools.request_traitement import traitement
from langchain_core.messages.ai import AIMessage
import OrderState

WELCOME_MSG = (
    "Bonjour ! Je suis votre assistant, comment puis-je vous aider?"
)

def database_agent(state: OrderState) -> OrderState:
    """The chatbot itself. A wrapper around the model's own chat interface."""

    if state['messages']:
        print(traitement(state['request_call']).to_string())
        new_output = {}
    else:
        new_output = {"messages" : [AIMessage(content=WELCOME_MSG)]}

    return state | new_output

