from Tools_nodes.database_tools.request_traitement import traitement
from langchain_core.messages.ai import AIMessage
import OrderState

WELCOME_MSG = (
    "Bonjour ! Je suis votre assistant, comment puis-je vous aider?"
)

def database_agent(state: OrderState) -> OrderState:
    """The chatbot itself. A wrapper around the model's own chat interface."""

    message = ""

    state['dataFrames'] = []
    state['dataFrames_columns'] = []
    
    for element_cherche in state['request_call'].elements_cherches_request:
        (dataframes, fields_alias_contexte) = traitement(element_cherche)

        for (dataFrame_index) in dataframes:
            state['dataFrames'].append(dataframes[dataFrame_index])
            message += dataframes[dataFrame_index].to_html()

        state['dataFrames_columns'] += fields_alias_contexte

    new_output = {"messages" : [AIMessage(content=message)]}

    return state | new_output

