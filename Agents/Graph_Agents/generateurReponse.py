from typing import Literal
from langchain_core.messages.ai import AIMessage
from OrderState import OrderState
from model import model


AGENT_GENERATION_SYSINT = (
    '''Génère une réponse à partir du message qu'on te donne. Tu convertis la réponse json en un texte qu'un humain peut comprendre. Le texte doit fournir la réponse à la question qui a été posée à la base. Ne pas parler de requête json parce que je comprends rien et je hais l'informatique.'''
)

def generer_reponse(state: OrderState) -> OrderState:
    """The chatbot itself. A wrapper around the model's own chat interface."""

    # If there are messages, continue the conversation with the Mistral model.
    print(state["question"] + state["tools_to_answer"])
    new_output = model.invoke([AGENT_GENERATION_SYSINT] + state["question"] + state["tools_to_answer"])

    return state | {"messages": [new_output]}
