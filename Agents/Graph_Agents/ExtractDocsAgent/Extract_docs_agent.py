from OrderState import OrderState
from model import model_codestral

from Graph_Agents.ExtractDocsAgent.request_format import request
from Graph_Agents.Agent import Agent

class Extract_docs_agent(Agent):
    def __init__(self):
        self.structured_llm = model_codestral.with_structured_output(request, include_raw = True)

    def interaction(self, state: OrderState) -> OrderState:
        """The chatbot itself. A wrapper around the model's own chat interface."""

        #Agent chargé de formaliser sous la forme d'une requête l'information à chercher
        # Appel du modèle structuré
        req = self.structured_llm.invoke(state['information_chercher'])

        input_token, output_token = self.obtenir_tokens(req['raw'])
        state['input_tokens'] += input_token
        state['output_tokens'] += output_token
        
        state['prix_input_tokens'] += input_token * 0.3 / 10 ** 6
        state['prix_output_tokens'] += output_token * 0.9 / 10 ** 6

        # ✅ Stocker proprement
        state['request_call'] = req['parsed']
        state['request_call_initial'] = req['parsed']
        print("➡️ Requête extraite :", req['parsed'])
        print("📦 State keys: EXTRACT_DOC", list(state.keys()))
        return state

