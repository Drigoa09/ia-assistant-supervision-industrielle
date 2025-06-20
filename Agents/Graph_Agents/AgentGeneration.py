from langchain_core.messages.ai import AIMessage
from OrderState import OrderState
from typing import Literal
from model import model
from langgraph.graph import StateGraph, START, END

AGENT_GENERATION_SYSINT = (
    '''Tu es un assistant expert chargé de classifier des questions d'utilisateurs industriels.

Ta tâche est simple :
→ Détermine si la question concerne directement des **données machines indexées dans Elasticsearch** (temps, température, consommation, variables de fonctionnement...).
→ Ou si la question relève de la **documentation technique, d’une explication de concept, ou d’une aide générale**.

---

Si la question concerne :
- des mesures collectées par capteurs
- des machines nommées (ex : Huron, Techplus)
- des variables techniques (température, vitesse, état, programme)
- des périodes temporelles (semaine, aujourd’hui, hier, etc.)

Alors tu réponds simplement :
**TRUE**  ← la question est liée aux données indexées

Sinon :
**FALSE** ← la question relève de la documentation, d’un guide ou d’une aide

---

### Exemples :

1. "Quel est le temps de cycle moyen de la Huron KXFive sur les 7 derniers jours ?"  
→ **TRUE**

2. "À quoi sert le protocole OPCUA ?"  
→ **FALSE**

3. "Quelle est la consommation électrique du robot Techplus cette semaine ?"  
→ **TRUE**

4. "Comment interpréter l’état S7 d’un automate ?"  
→ **FALSE**

5. "Quelles machines ont le plus d’arrêts depuis hier ?"  
→ **TRUE**

6. "Explique-moi comment créer un dashboard dans Grafana."  
→ **FALSE**

---

### Maintenant, traite cette question :
{question}
Et réponds **uniquement** par `TRUE` ou `FALSE`, sans rien ajouter.
'''
)

WELCOME_MSG = (
    "Bonjour ! Je suis votre assistant, comment puis-je vous aider?"
)


def chatbot_with_welcome_msg(state: OrderState) -> OrderState:
    """The chatbot itself. A wrapper around the model's own chat interface."""

    if state["messages"]:
        # If there are messages, continue the conversation with the Mistral model.
        new_output = model.invoke([AGENT_GENERATION_SYSINT] + state["messages"])
        state["question"] = [state["messages"][-1]] 
        state["tools_to_answer"] = [] 
        state['Trois'] = False
    else:
        # If there are no messages, start with the welcome message.
        new_output = AIMessage(content=WELCOME_MSG)

    return state | {"messages": [new_output]}

def maybe_route_to_extract_docs(state: OrderState) -> Literal["erreur", "extract_docs", "human"]:
    """Route to the chatbot, unless it looks like the user is exiting."""

    if not (msgs := state.get("messages", [])):
        raise ValueError(f"No messages found when parsing state: {state}")

    # Only route based on the last message.
    msg = msgs[-1].content

    if msg == WELCOME_MSG:
        return "human"

    # When the chatbot returns tool_calls, route to the "tools" node.
    if "TRUE" in msg:
        return "extract_docs"
    else:
        return "erreur"