from langchain_core.messages.ai import AIMessage
from ..OrderState import OrderState # Changed to relative
from typing import Literal
from ..model import model # Changed to relative
from langgraph.graph import StateGraph, START, END

def afficher_erreur(state: OrderState) -> OrderState:
    """The chatbot itself. A wrapper around the model's own chat interface."""

    return state | {"messages": ["Erreur !"]}
