from OrderState import OrderState
from model import model_codestral

from Tools_nodes.database_node.request_traitement import request
from Agent import Agent
class Extract_docs_agent(Agent):
    def __init__(self):
        self.structured_llm = model_codestral.with_structured_output(request, include_raw = True)

    def interaction(self, state: OrderState) -> OrderState:
        """The chatbot itself. A wrapper around the model's own chat interface."""

        #Agent chargé de formaliser sous la forme d'une requête l'information à chercher
        # Appel du modèle structuré
        req = self.structured_llm.invoke(state['information_chercher'])

        state['input_tokens'], state['output_tokens'] = self.obtenir_tokens(req['raw'])

        # ✅ Stocker proprement
        state['request_call'] = req['parsed']
        state['request_call_initial'] = req['parsed']
        print("➡️ Requête extraite :", req['parsed'])
        print("📦 State keys: EXTRACT_DOC", list(state.keys()))
        return state
