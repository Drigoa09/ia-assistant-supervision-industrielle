from typing import List
from pydantic import BaseModel, Field
from typing import Optional, List
from OrderState import OrderState
from model import model_codestral, model_mistral_medium
from Graph_Agents.CreateurTache.CreateurTache_Prompt import AGENT_JOB

from Graph_Agents.Agent import Agent
        
class CreateurTache(Agent):
        
    def __init__(self, Separation : BaseModel):
        #Model forcé à envoyer une réponse structurée sous la forme de Separation
        self.structured_llm = model_mistral_medium.with_structured_output(Separation, include_raw=True)
        #Créateur de tâches 

    def interaction(self, state: OrderState) -> OrderState:
        """The chatbot itself. A wrapper around the model's own chat interface."""

        #Appel à structured_llm
        new_output = self.structured_llm.invoke([AGENT_JOB, state['question']])

        state['input_tokens'], state['output_tokens'] = self.obtenir_tokens(new_output['raw'])

        state['information_chercher'] = new_output['parsed'].INFORMATION_CHERCHER

        #Affichage de la réponse de structured_llm
        print(f"Information cherchée : {new_output['parsed'].INFORMATION_CHERCHER} \n")
        
        if hasattr(new_output['parsed'], 'TRAITEMENT') and new_output['parsed'].TRAITEMENT != None:
            state['traitements'] = new_output['parsed'].TRAITEMENT

            self.afficher_traitement(new_output['parsed'])
        
        else:
            state['traitements'] = []

        return state
    
    def afficher_traitement(self, message):
        n = len(message.TRAITEMENT)
        msg_traitement = ""
        for i in range(n):
            msg_traitement += f"Traitement effectué {i + 1} : " + message.TRAITEMENT[i] + "\n"

        print(msg_traitement + "\n")
    
    
