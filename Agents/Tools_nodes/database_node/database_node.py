from Tools_nodes.database_node.request_traitement import traitement
from langchain_core.messages.ai import AIMessage
import OrderState

import pandas as pd

class DataFrameRole:

    def __init__(self, dataFrame, role):
        self.dataFrame = dataFrame
        self.role = role

def database_agent(state: OrderState) -> OrderState:
    """The chatbot itself. A wrapper around the model's own chat interface."""

    message = ""

    state['dataFrames'] = []
    
    for element_cherche in state['request_call'].elements_cherches_request:
        (dataframes, fields_role) = traitement(element_cherche)

        i = 0
        for (dataFrame_index) in dataframes:
            state['dataFrames'].append(DataFrameRole(dataFrame=dataframes[dataFrame_index], role = fields_role[i]))
            message += dataframes[dataFrame_index].to_html()

            i += 1

    new_output = {"messages" : [AIMessage(content=message)]}

    state['i'] = -1
    print("📦 State keys: DATABASE", list(state.keys()))
    return state | new_output

