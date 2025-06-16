from datetime import datetime
from time import timezone
from OrderState import OrderState
from typing import Literal
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage, AIMessage
    
def human_node(state: OrderState) -> OrderState:
    last_msg = state["messages"][-1]

    #state["messages"][-1] += "Nous sommes " + datetime.now(timezone.utc).isoformat()

    if isinstance(last_msg, AIMessage):
        print("[Modèle]:", last_msg.content)
        # ❗ Marque la fin pour empêcher la boucle
        state["finished"] = True
    elif isinstance(last_msg, HumanMessage):
        print("[Utilisateur]:", last_msg.content) 
    return state

def maybe_exit_human_node(state: OrderState) -> Literal["extract_docs", "__end__"]:
    if state.get("finished", False):
        return END
    return "extract_docs"

    