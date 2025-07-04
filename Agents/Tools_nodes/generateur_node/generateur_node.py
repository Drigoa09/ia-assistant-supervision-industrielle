from OrderState import OrderState

from pydantic import BaseModel, Field

from typing import List

from langchain_core.messages.ai import AIMessage


def choisir_dataFrame(dataFrames, args):

    new_dataFrames = []

    for arg in args:
        new_dataFrames.append(dataFrames[arg.numero_dataFrame])

    return new_dataFrames

def generateur_node(state: OrderState) -> OrderState:

    new_dataFrames = choisir_dataFrame(state['dataFrames'], state['request_call'].choix_dataFrames)

    message = ""

    for (dataFrame_index) in new_dataFrames:
        message += dataFrame_index.dataFrame.to_html()

    #new_output = {"messages" : [AIMessage(content=message)]}
    print("📦 State après traitement:", list(state.keys()))
    return {
            **state,
            "messages": state["messages"] + [AIMessage(content=message)]
        }
