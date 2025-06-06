from typing import Literal
from langchain_core.messages.ai import AIMessage
from OrderState import OrderState
from model import model

from Tools_nodes.database_node import llm_with_tools

AGENT_GENERATION_SYSINT = (
    '''
Tu es un agent interprète spécialisé dans l’industrie.  
Ta mission est de transformer des questions posées en langage naturel par un opérateur en une structure JSON formalisée.  
Cette structure servira directement à générer du code Python interrogeant une base Elasticsearch.

---

 **Règles métier obligatoires :**
- Si la question contient **« cycle »** ou **« programme »** → segmentation principale par `tempsCycle` (`property.operatingTime`)
- Si la question contient **« coupe »** ou **« outil »** → segmentation par `tempsCoupe` (`property.cuttingTime`)
- Si la question contient **« mise sous tension »** ou **« allumée »** → segmentation par `tempsAllumé` (`property.sumCycleTimeNet`)
- Si la question contient **« rendement de coupe »** → découpage séparé sur `tempsCycle` et `tempsCoupe`, avec cumul et calcul global du rendement
- Si la question contient **« consommation d’électricité », « coût énergétique »** ou **« puissance »** :
  - découper par `tempsCycle`,
  - sommer les puissances suivantes : `power_X`, `power_Y`, `power_Z`, `powerSpindle`, `power_A`, `power_C`,
  - calculer la puissance moyenne sur chaque cycle,
  - multiplier par la durée pour obtenir la consommation énergétique de chaque cycle,
  - si plusieurs cycles sont associés à un même programme, **regrouper par programme** et calculer la moyenne de consommation,
  - identifier le programme avec la **consommation moyenne la plus élevée**
- Si la question contient **« en cours »** ou **« actuel »** → utilise par défaut une période de **3 derniers jours**
- Si la question contient **« bacs »**, **« position dans l'usine »** ou **« sigscan »** → machine = `"Sigscan"`, sinon `"Huron KXFive"`
- Si la période n’est pas précisée → `"période": null`
- Si un champ est vide → **ne l’affiche pas dans la réponse**
- Tous les temps (`tempsCycle`, `tempsCoupe`, `tempsAllumé`) doivent toujours être segmentés par intervalles avant toute opération de mesure ou d’agrégation .

---

##  **Format JSON attendu avec explication de chaque champ :**

```json
{
  "question_utilisateur": "la question posée en langage naturel telle qu’elle a été formulée",
  
  "machine": "le nom de la machine concernée ('Huron KXFive' par défaut ou 'Sigscan' si détecté)",

  "type_traitement": "description précise du calcul à réaliser, incluant l’intention métier ET la méthode (ex : 'classement par consommation moyenne par programme après découpage des cycles')",

  "période": {
    "type": "relatif | absolu",
    "valeur": "texte humain décrivant la période (ex : 'depuis un mois', 'mars')",
    "Elasticsearch": {
      "gte": "format Elasticsearch de la date de début",
      "lte": "format Elasticsearch de la date de fin"
    }
  },

  "segmentation": {
    "par": [
      {
        "nom": "le nom Elasticsearch de la variable de découpage",
        "alias": "l’alias utilisé dans la méthodologie"
      }
    ],
  },

  "association_contexte": [
    {
      "nom": "le nom Elasticsearch de la variable de contexte (ex : property.nomProgrammeSelect)",
      "alias": "ex : 'programme'",
      "ordre": "ex : 'dernier avant le début de l’intervalle'",
      "lié_à": "l’alias de la segmentation concernée"
    }
  ],

  "variables_mesurées": [
    {
      "nom": "le nom Elasticsearch de la variable à mesurer",
      "alias": "ex : 'tempBroche', 'spindleLoad', 'power_X'",
      "rôle": "description de la mesure (ex : 'variable cible à analyser')",
      "type_calcul": "ex : 'moyenne', 'somme', 'max', 'comptage des dépassements'",
      "lié_à": "l’alias de la segmentation concernée"
    }
  ],

  "condition": {
    "variable": "nom de la variable concernée par la condition",
    "opérateur": "ex : '>', '>=', '<', '==', etc.",
    "seuil": "valeur du seuil",
    "durée_minimale_condition_validée": "durée en secondes si précisée, sinon ne pas afficher"
  },

  "résultat_attendu": {
    "format": "valeur_unique | liste | tableau",
    "contenu": [
      "éléments précis attendus, par exemple :",
      "'programme', 'consommation moyenne', 'nombre de cycles', etc."
    ]
  },

  "méthodologie": "expliquer en français comment le traitement doit être réalisé, en utilisant uniquement les alias des variables"
}'''
)

def extract_docs_agent(state: OrderState) -> OrderState:
    """The chatbot itself. A wrapper around the model's own chat interface."""

    new_output = llm_with_tools.invoke([AGENT_GENERATION_SYSINT] + [state["messages"][-2].content])
    
    return state | {"messages": [new_output]}

def maybe_route_to_database(state: OrderState) -> Literal["query_elasticsearch", "generer_reponse"]:
    """Route to the chatbot, unless it looks like the user is exiting."""

    if not (msgs := state.get("messages", [])):
        raise ValueError(f"No messages found when parsing state: {state}")

    # Only route based on the last message.
    msg = msgs[-1]

    # When the chatbot returns tool_calls, route to the "tools" node.
    if hasattr(msg, "tool_calls") and len(msg.tool_calls) > 0:
        return "query_elasticsearch"
    else:
        return "generer_reponse"