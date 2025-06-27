from OrderState import OrderState
from model import model_codestral

from Tools_nodes.database_tools.request_format import request

structured_llm = model_codestral.with_structured_output(request)

def extract_docs_agent(state: OrderState) -> OrderState:
    """The chatbot itself. A wrapper around the model's own chat interface."""

    #Agent chargé de formaliser sous la forme d'une requête l'information à chercher
    # Appel du modèle structuré
    req = structured_llm.invoke(state['information_chercher'])

    # ✅ Stocker proprement
    state['request_call'] = req
    state['request_call_initial'] = req
    print("➡️ Requête extraite :", req)
    print("📦 State keys: EXTRACT_DOC", list(state.keys()))
    return state
