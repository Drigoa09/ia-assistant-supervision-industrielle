from typing import List
from pydantic import BaseModel, Field
from typing import Optional, List
from OrderState import OrderState
from model import model_codestral, model_mistral_medium
from Graph_Agents.Prompts.CreateurTache_Prompt import AGENT_JOB
from Tools_nodes.database_tools.request_format import request

#Forme de la réponse voulue donnée par l'agent
class Separation(BaseModel):
    """Sépare un texte pour en obtenir l'information à chercher et le traitement fait sur l'information.
    Les données contenues dans les attributs doivent être des phrases
    """

    INFORMATION_CHERCHER : str = Field(description = "Information recherchée dans la base de donnée. Exprimé sous forme d'un ordre.")
    TRAITEMENT : Optional[List[str]] = Field(default= None, description = "Traitements faits sur les informations de la base de donnée déduit à partir de la question. Exprimé sous forme d'un ordre")
#Model forcé à envoyer une réponse structurée sous la forme de Separation
structured_llm = model_mistral_medium.with_structured_output(Separation)
#Créateur de tâches 
def createur_tache(state: OrderState) -> OrderState:
    """The chatbot itself. A wrapper around the model's own chat interface."""

    #Appel à structured_llm
    new_output = structured_llm.invoke([AGENT_JOB, state['question']])

    state['information_chercher'] = new_output.INFORMATION_CHERCHER

    #Affichage de la réponse de structured_llm
    print(f"Information cherchée : {new_output.INFORMATION_CHERCHER} \n")
    
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
