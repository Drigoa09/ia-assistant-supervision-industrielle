from langchain_core.messages.ai import AIMessage
from ..OrderState import OrderState # Changed to relative
from ..model import model # Changed to relative

AGENT_GENERATION_SYSINT = (
    '''
    Tu es un agent expert qui doit évaluer si un ensemble de documents extraits permet de répondre correctement à une question industrielle posée par un opérateur.

Tu as 3 niveaux possibles de jugement :

- **"Correct"** : les documents apportent une réponse claire, complète, sans contradiction à la question.
- **"Ambigu"** : les documents sont partiellement liés à la question, mais il y a des imprécisions, des éléments manquants, ou une ambiguïté dans l’interprétation.
- **"Incorrect"** : les documents ne permettent pas de répondre à la question, ou sont hors sujet, ou contradictoires.

---

Critères à prendre en compte :
- les **variables clés** ou concepts évoqués dans la question sont-ils bien présents ?
- la **période temporelle** ou le contexte demandé est-il traité ?
- les documents permettent-ils à un opérateur **de prendre une décision ou de conclure** ?

---

### Format de sortie strict :

```json
{
  "classification": "Correct" | "Ambigu" | "Incorrect",
  "justification": "phrase claire justifiant la classification"
}

'''
)

def evaluation_docs_agent(state: OrderState) -> OrderState:
    """The chatbot itself. A wrapper around the model's own chat interface."""

    # If there are messages, continue the conversation with the Mistral model.

    new_output = model.invoke([AGENT_GENERATION_SYSINT] + [state["messages"][-2].content])

    return state | {"messages": [new_output]}