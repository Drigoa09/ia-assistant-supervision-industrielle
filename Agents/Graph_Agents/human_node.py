from datetime import datetime
from time import timezone
from OrderState import OrderState
from typing import Literal
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage, AIMessage

WELCOME_MSG = (
    "Bonjour ! Je suis votre assistant, comment puis-je vous aider?"
)

def human_node(state: OrderState) -> OrderState:
    if state["messages"]:
        last_msg = state["messages"][-1]
    else:
        last_msg = WELCOME_MSG
        state["messages"] += [AIMessage(WELCOME_MSG)]

    
    """Display the last model message to the user, and receive the user's input."""
    print("Model:", last_msg)

    user_input = input("User: ")

    # If it looks like the user is trying to quit, flag the conversation
    # as over.
    if user_input in {"q", "quit", "exit", "goodbye"}:
        state["finished"] = True

    state['question'] = user_input

    return state | {"messages": [HumanMessage(user_input)]}
    #state["messages"][-1] += "Nous sommes " + datetime.now(timezone.utc).isoformat()

    if isinstance(last_msg, AIMessage):
        #print("[Modèle]:", last_msg.content)
        # ❗ Marque la fin pour empêcher la boucle
        state["finished"] = True
    elif isinstance(last_msg, HumanMessage):
        print("[Utilisateur]:", last_msg.content) 
    return state

    '''
    """Display the last model message to the user, and receive the user's input."""
    last_msg = state["messages"][-1]
    print("Model:", last_msg.content)

    user_input = input("User: ")

    # If it looks like the user is trying to quit, flag the conversation
    # as over.
    if user_input in {"q", "quit", "exit", "goodbye"}:
        state["finished"] = True

    return state | {"messages": [HumanMessage(user_input)]}
    '''

def maybe_exit_human_node(state: OrderState) -> Literal["createurTache", "__end__"]:
    if state.get("finished", False):
        return END
    return "createurTache"

    