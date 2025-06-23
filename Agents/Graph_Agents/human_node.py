from langchain_core.messages import HumanMessage, AIMessage
from OrderState import OrderState
from typing import Literal
from langgraph.graph import END
from langchain_core.messages import HumanMessage, AIMessage

WELCOME_MSG = "Bonjour ! Je suis votre assistant, comment puis-je vous aider?"

def human_node(state: OrderState) -> OrderState:
    if not state["messages"]:
        # Premier tour : injecter le message de bienvenue
        state["messages"].append(AIMessage(content=WELCOME_MSG))
        state["finished"] = True  # Stopper pour éviter de re-boucler
        return state

    last_msg = state["messages"][-1]

    if isinstance(last_msg, AIMessage):
        state["finished"] = True
    elif isinstance(last_msg, HumanMessage):
        print("[Utilisateur]:", last_msg.content)
        state["question"] = last_msg.content

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

def maybe_exit_human_node(state: OrderState) -> Literal["Créateur de tâches", "__end__"]:
    if state.get("finished", False):
        return END
    return "Créateur de tâches"

    