from OrderState import OrderState

from pydantic import BaseModel, Field

from typing import List

from langchain_core.messages.ai import AIMessage


# Fonction permettant de chosir les Dataframes qui seront afficher à l'utilisateur
def choisir_dataFrame(dataFrames, args):

    new_dataFrames = []

    for arg in args:
        new_dataFrames.append(dataFrames[arg.numero_dataFrame])

    return new_dataFrames

def generateur_node(state: OrderState) -> OrderState:
    # Choix des dataframes à afficher
    new_dataFrames = choisir_dataFrame(state['dataFrames'], state['request_call'].choix_dataFrames)

    message = ""
    # Concaténation des Dataframes en HTML pour l'affichage
    for (dataFrame_index) in new_dataFrames:
        message += dataFrame_index.dataFrame.to_html()

    #new_output = {"messages" : [AIMessage(content=message)]}
    print("📦 State après traitement:", list(state.keys()))
    # On retourne le nouvel état prêt avec ajout du nouveau message en HTML dans state["messages"]
    return {
            **state,
            "messages": state["messages"] + [AIMessage(content=message)]
        }

