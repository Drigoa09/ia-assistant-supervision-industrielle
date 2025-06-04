from langchain_core.messages.ai import AIMessage
from OrderState import OrderState
from typing import Literal
from model import model
from langgraph.graph import StateGraph, START, END

def afficher_erreur(state: OrderState) -> OrderState:
    """The chatbot itself. A wrapper around the model's own chat interface."""

    return state | {"messages": ["Erreur !"]}
