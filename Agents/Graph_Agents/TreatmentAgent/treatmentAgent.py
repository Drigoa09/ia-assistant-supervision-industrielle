from Graph_Agents.Agent import Agent
from OrderState import OrderState
from model import model_codestral, model_mistral_medium

from Tools_nodes.treatment_node.traitement_format import Traitement_Format, fonction

class TreatmentAgent(Agent):

    def __init__(self, fonction, prompt_job, exemples):

        self.structured_llm = model_codestral.with_structured_output(fonction, include_raw=True)
        self.prompt_job = prompt_job
        self.exemples = exemples

    def interaction(self, state: OrderState) -> OrderState:
        """Agent de traitement"""

        if state['traitement'] != None:
            prompt = self.creer_prompt(state['dataFrames'], state['traitement'])

            print("Prompt donné : \n\n" + prompt)

        # Appelle le modèle avec prompt fusionné
        traitement_format_result = self.structured_llm.invoke(prompt)

        input_token, output_token = self.obtenir_tokens(traitement_format_result['raw'])
        state['input_tokens'] += input_token
        state['output_tokens'] += output_token
        
        state['prix_input_tokens'] += input_token * 0.3 / 10 ** 6
        state['prix_output_tokens'] += output_token * 0.9 / 10 ** 6
    

        #print("🧪 Résultat traitement_format:", traitement_format_result)

        # Tu crées un NOUVEAU dict propre ici
        updated_state = {
            **state,
            "traitement_format": traitement_format_result['parsed']
        }

        #print("📤 Ce que je retourne dans treatment_agent:", list(updated_state.keys()))

        return updated_state
    
    def creer_prompt(self, dataFrames, traitement_actuel):
        job_message = self.prompt_job
        job_message += self.ajouter_cles_dataFrames(dataFrames)
        job_message += self.exemples
        job_message += f"\n{traitement_actuel}"

        return job_message
         
    
    def ajouter_cles_dataFrames(self, dataFrames):
        
        n = len(dataFrames)

        job_message = ""

        for i in range(n):
                job_message +=  f"Emplacement : {i} et colonnes : {dataFrames[i].dataFrame.columns}" + " : " + dataFrames[i].role + "\n"

        job_message += '''Tu ne peux utiliser que ces clés de dataFrame. Il n'est pas possible d'en utiliser des variantes'''

        return job_message



