from typing import List
from pydantic import BaseModel, Field
from typing import Optional, List
from OrderState import OrderState
from model import model_codestral, model_mistral_medium
from Graph_Agents.CreateurTache.CreateurTache_Prompt import AGENT_JOB

from Agent import Agent
        
class CreateurTache(Agent):
        
    def __init__(self, Separation : BaseModel):
        #Model forcé à envoyer une réponse structurée sous la forme de Separation
        self.structured_llm = model_mistral_medium.with_structured_output(Separation, include_raw=True)
        #Créateur de tâches 

    def interaction(self, state: OrderState) -> OrderState:
        """The chatbot itself. A wrapper around the model's own chat interface."""

        #Appel à structured_llm
        new_output = self.structured_llm.invoke([AGENT_JOB, state['question']])
        
        state['input_tokens'] += (new_output['raw'].usage_metadata['input_tokens'])
        state['output_tokens'] += (new_output['raw'].usage_metadata['output_tokens'])

        state['input_tokens'], state['output_tokens'] = self.obtenir_tokens(new_output['raw'])

        state['information_chercher'] = new_output['parsed'].INFORMATION_CHERCHER

        #Affichage de la réponse de structured_llm
        print(f"Information cherchée : {new_output['parsed'].INFORMATION_CHERCHER} \n")
        
        if hasattr(new_output['parsed'], 'TRAITEMENT') and new_output['parsed'].TRAITEMENT != None:
            state['traitements'] = new_output['parsed'].TRAITEMENT

            n = len(new_output['parsed'].TRAITEMENT)
            msg_traitement = ""
            for i in range(n):
                msg_traitement += f"Traitement effectué {i + 1} : " + new_output['parsed'].TRAITEMENT[i] + "\n"

            print(msg_traitement + "\n")
        
        else:
            state['traitements'] = []

        return state
    
    def obtenir_tokens(self, message):
        
        return (message.usage_metadata['input_tokens'], message.usage_metadata['output_tokens'])
    
    
