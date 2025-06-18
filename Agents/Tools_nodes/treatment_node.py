from langchain_core.messages.ai import AIMessage

from Tools_nodes.treatment_tools.traitement_format import fonctions_existantes

import OrderState

def plus_occurent(dataFrames, args):

    new_dataFrames = []

    for arg in args:
        for dataFrame in dataFrames:
            if arg in dataFrame.columns:
                new_dataFrames.append(dataFrame[arg].value_counts())
                break

    return new_dataFrames
    


def treatment_node(state: OrderState) -> OrderState:
    """The chatbot itself. A wrapper around the model's own chat interface."""

    fonctions_appelees = state['request_call'].fonctions_appelees

    new_dataFrames = []

    for fonction_appelee in fonctions_appelees:
        
        if fonction_appelee.fonction_appelee == fonctions_existantes.PLUS_OCCURENT:

            new_dataFrames += plus_occurent(state['dataFrames'], fonction_appelee.args)

    message = ""

    for (dataFrame_index) in new_dataFrames:
        message += dataFrame_index.to_html()

    new_output = {"messages" : [AIMessage(content=message)]}

    return state | new_output