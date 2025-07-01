from OrderState import OrderState
from model import model_codestral

from Tools_nodes.database_tools.request_format import request

from devtools import pprint

structured_llm = model_codestral.with_structured_output(request, include_raw = True)

def extract_docs_agent(state: OrderState) -> OrderState:
    """The chatbot itself. A wrapper around the model's own chat interface."""

    #Agent chargé de formaliser sous la forme d'une requête l'information à chercher
    # Appel du modèle structuré
    req = structured_llm.invoke(state['information_chercher'])

    state['input_tokens'] += (req['raw'].usage_metadata['input_tokens'])
    state['output_tokens'] += (req['raw'].usage_metadata['output_tokens'])

    # ✅ Stocker proprement
    state['request_call'] = req['parsed']
    state['request_call_initial'] = req['parsed']
    print("➡️ Requête extraite :", req['parsed'])
    print("📦 State keys: EXTRACT_DOC", list(state.keys()))
    return state
