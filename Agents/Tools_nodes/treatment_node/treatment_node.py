from langchain_core.messages.ai import AIMessage

from Tools_nodes.treatment_node.traitement_format import fonctions_existantes

import OrderState

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from Tools_nodes.database_node.database_node import DataFrameRole

from Tools_nodes.treatment_node.fonction_appelees import D

def treatment_node(state: OrderState) -> OrderState:
    """The chatbot itself. A wrapper around the model's own chat interface."""
    print("📦 State reçu dans treatment_node:", list(state.keys()))
    print("🔍 traitement_format vaut:", state.get("traitement_format"))

    if state['traitement'] != None:

        # Tentative de récupération sécurisée
        traitement_format = state.get("traitement_format")
        if traitement_format is None:
            raise ValueError("❌ traitement_format est totalement absent, même en fallback ! Clés disponibles : " + str(state.keys()))

        new_dataFrames = []

        fonction_appelee = traitement_format

        if fonction_appelee.fonction_appelee == fonctions_existantes.CREER_GRAPHIQUE:
            state['figure'] = D[fonction_appelee.fonction_appelee](state['dataFrames'], fonction_appelee.args)
        else:
            new_dataFrames += D[fonction_appelee.fonction_appelee](state['dataFrames'], fonction_appelee.args)
            state['dataFrames'] = new_dataFrames

        message = ""

        for (dataFrame_index) in new_dataFrames:
            message += dataFrame_index.dataFrame.to_html()

        #new_output = {"messages" : [AIMessage(content=message)]}
        print("📦 State après traitement:", list(state.keys()))
        return {
                **state,
                "messages": state["messages"] + [AIMessage(content=message)]
            }
    
    else:
        
        return state