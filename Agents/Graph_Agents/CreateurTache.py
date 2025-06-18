from typing import List
from pydantic import BaseModel, Field

from model import model

from enum import Enum
from typing import Optional, List

from typing import Literal
from langchain_core.messages import AIMessage, HumanMessage
from OrderState import OrderState
from model import model

AGENT_JOB = '''
Tu es chargé de séparer une question pour en extraire l'information cherchée et le traitement à effectuer
sur cette information. Exprime l'information cherchée et le traitement sous la forme d'un ordre.

L'information cherchée peut être :
- Trouvée entre deux dates précises.
Les traitements possibles sont :
- Trouver les occurences des éléments parmi l'information cherchée
- Rien faire si aucun traitement n'est demandé
'''

class Separation(BaseModel):
    """Sépare un texte pour en obtenir l'information à chercher et le traitement fait sur l'information.
    Les données contenues dans les attributs doivent être des phrases
    """

    INFORMATION_CHERCHER : str = Field(description = "Information recherchée dans la base de donnée. Exprimé sous forme d'un ordre")
    TRAITEMENT : Optional[str] = Field(description = "Traitement fait sur les informations de la base de donnée déduit à partir de la question. Rien ajouter de plus. Exprimé sous forme d'un ordre") 

structured_llm = model.with_structured_output(Separation)

def createur_tache(state: OrderState) -> OrderState:
    """The chatbot itself. A wrapper around the model's own chat interface."""

    new_output = structured_llm.invoke([AGENT_JOB, state['question']])

    state['information_chercher'] = new_output.INFORMATION_CHERCHER

    print("Information cherchée : " + new_output.INFORMATION_CHERCHER + "\n")
    
    if hasattr(new_output, 'TRAITEMENT') and new_output.TRAITEMENT != None:
        state['traitement'] = new_output.TRAITEMENT
        print("Traitement effectué : " + new_output.TRAITEMENT + "\n")
    
    else:
        state['traitement'] = None

    return state
