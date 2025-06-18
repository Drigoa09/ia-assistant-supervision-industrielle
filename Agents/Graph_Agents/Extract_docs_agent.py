from typing import Literal
from langchain_core.messages.ai import AIMessage
from OrderState import OrderState
from model import model_codestral

AGENT_GENERATION_SYSINT = (
    '''
Tu es un agent interprète spécialisé dans l’industrie.

Tu essaies de répondre aux questions avec les outils qui te sont donnés, pas à pas. 
''')

from langgraph.prebuilt import create_react_agent

from Tools_nodes.database_tools.request_format import request

structured_llm = model_codestral.with_structured_output(request)

def extract_docs_agent(state: OrderState) -> OrderState:
    """The chatbot itself. A wrapper around the model's own chat interface."""

    state['request_call'] = structured_llm.invoke(state['information_chercher'])

    print(state['request_call'])

    return state

def maybe_route_to_database(state: OrderState) -> Literal["query_elasticsearch", "generer_reponse"]:
    """Route to the chatbot, unless it looks like the user is exiting."""

    if not (msgs := state.get("messages", [])):
        raise ValueError(f"No messages found when parsing state: {state}")

    # Only route based on the last message.
    msg = msgs[-1]

    # When the chatbot returns tool_calls, route to the "tools" node.
    if hasattr(msg, "tool_calls") and len(msg.tool_calls) > 0:
        return "query_elasticsearch"
    else:
        return "generer_reponse"