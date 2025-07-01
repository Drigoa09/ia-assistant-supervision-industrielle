from OrderState import OrderState

from model import model_mistral_medium
from pydantic import BaseModel, Field

from typing import List

class Element(BaseModel):

    numero_dataFrame : int = Field(description = "Numéro du dataFrame où est contenu l'élément")

class Choix(BaseModel):

    choix_dataFrames : List[Element] = Field(description="Choix des dataFrames à afficher")

model_with_structured_output = model_mistral_medium.with_structured_output(Choix, include_raw=True)

def generer_reponse(state: OrderState) -> OrderState:
    
    AGENT_JOB = f'''Tu es un agent chargé de répondre à la question {state["question"]}.

    Voici ce qui a été fait avant que tu reçoives les informations :*
    Information cherchée : {state['information_chercher']}
    Traitements : {state['traitements']}

    Pour cela tu as plusieurs données disponibles. Ces données sont représentées par des DataFrames

    Voici leurs informations :

    '''

    n = len(state['dataFrames'])
        
    for i in range(n):
        AGENT_JOB +=  f"Emplacement : {i} et colonnes : {state['dataFrames'][i].dataFrame.columns}" + " : " + state['dataFrames'][i].role + "\n"

    AGENT_JOB += '''

    Tu dois choisir lesquelles des DataFrames il faut afficher.
    L'humain qui regardera n'aime pas voir des informations inutiles. Il est con et s'énerve vite.
    Fait en sorte de donner le plus d'informations possible en donnant le moins de DataFrame possibles.
    L'humain est con et n'aime pas lire trop de choses. Va à l'essentiel, putain !
    '''

    request = model_with_structured_output.invoke([AGENT_JOB])

    state['input_tokens'] += (request['raw'].usage_metadata['input_tokens'])
    state['output_tokens'] += (request['raw'].usage_metadata['output_tokens'])

    print(request['parsed'])

    state['request_call'] = request['parsed']

    return state

