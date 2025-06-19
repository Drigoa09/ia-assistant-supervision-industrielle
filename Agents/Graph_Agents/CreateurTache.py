from typing import List
from pydantic import BaseModel, Field

from enum import Enum
from typing import Optional, List

from typing import Literal
from langchain_core.messages import AIMessage, HumanMessage
from OrderState import OrderState
from model import model_codestral

AGENT_JOB = '''
Tu es chargé de traiter une question pour en extraire l'information cherchée et les traitements à effectuer
sur cette information. Exprime l'information cherchée et les traitements sous la forme d'un ordre.
Il est possible que des traitements ne soit pas associé à une question. 

L'information cherchée doit toujours être demandée entre deux dates précises.
Les informations qu'il est possible de chercher sont : 
    - Les programmes
    - Les cycles
    - Les outils

Les traitements possibles sont :
- Trouver les occurences des éléments parmi l'information cherchée et les classer par ordre décroissant
- Exprimer une information en fonction d'une autre information
- Calculer la somme d'une information
- Diviser deux valeurs
- Filtrer une une colonne de DataFrames en fonction de critères

Documentation :
Comment calculer un rendement de coupe ?
Il faut tout d'abord extraire les temps de cycle et les temps où les machines sont allumées.
Ensuite, il faut calculer la somme des temps de cycle divisée par la somme des temps où les machines sont allumées.

Exemple 1 :
Trouver les programmes en fonction de leur cycle associé.

INFORMATION_CHERCHER='Trouver les programmes et les cycles' TRAITEMENT=['Exprimer les programmes en fonction de leur cycle associé']

Exemple 2 :
Trouver les outils en fonction de leur temps de coupe.

INFORMATION_CHERCHER='Trouver les outils et les temps de coupe' TRAITEMENT=['Exprimer les outils en fonction de leur temps de coupe associé']

Exemple 3 :
Trouver les programmes en fonction de leur cycle associé. Puis cherche le programme le plus utilisé.

INFORMATION_CHERCHER='Trouver les programmes et les cycles' TRAITEMENT=['Exprimer les programmes en fonction de leur cycle associé', 'Chercher le programme le plus utilisé']

Exemple 4 :
Trouver les outils utilisés dans le programme _N_OP20_AIR_SPF

INFORMATION_CHERCHER = 'Trouver les programmes, les cycles, les outils et les temps de coupe' TRAITEMENT = ['Exprimer les programmes en fonction de leur cycle associé et exprimer les outils en fonction de leur temps de coupe associé', 'Filtrer les outils en acceptant que ceux du programme _N_OP20_AIR_SPF']
'''

class Separation(BaseModel):
    """Sépare un texte pour en obtenir l'information à chercher et le traitement fait sur l'information.
    Les données contenues dans les attributs doivent être des phrases
    """

    INFORMATION_CHERCHER : str = Field(description = "Information recherchée dans la base de donnée. Exprimé sous forme d'un ordre")
    TRAITEMENT : Optional[List[str]] = Field(default= None, description = "Traitements faits sur les informations de la base de donnée déduit à partir de la question. Exprimé sous forme d'un ordre") 

structured_llm = model_codestral.with_structured_output(Separation)

def createur_tache(state: OrderState) -> OrderState:
    """The chatbot itself. A wrapper around the model's own chat interface."""

    new_output = structured_llm.invoke([AGENT_JOB, state['question']])

    state['information_chercher'] = new_output.INFORMATION_CHERCHER

    print("Information cherchée : " + new_output.INFORMATION_CHERCHER + "\n")
    
    if hasattr(new_output, 'TRAITEMENT') and new_output.TRAITEMENT != None:
        state['traitements'] = new_output.TRAITEMENT

        n = len(new_output.TRAITEMENT)
        msg_traitement = ""
        for i in range(n):
            msg_traitement += f"Traitement effectué {i + 1} : " + new_output.TRAITEMENT[i] + "\n"

        print(msg_traitement + "\n")
    
    else:
        state['traitements'] = []

    return state
