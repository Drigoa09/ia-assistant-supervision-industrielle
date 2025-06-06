from typing import Literal
from langchain_core.messages.ai import AIMessage
from OrderState import OrderState
from model import model

from Tools_nodes.database_node import llm_with_tools

AGENT_GENERATION_SYSINT = (
    '''
Tu es un agent interprète spécialisé dans l’industrie.    
Tu essaies de répondre à la question posée par l'utilisateur en utilisant les informations qui te sont données par les outils que tu as.
Si tu n'as pas assez d'informations, tu peux utiliser les outils que tu as.

'''
)

def extract_docs_agent(state: OrderState) -> OrderState:
    """The chatbot itself. A wrapper around the model's own chat interface."""

    new_output = llm_with_tools.invoke([AGENT_GENERATION_SYSINT] + state["question"] + state["tools_to_answer"])
    state["tools_to_answer"] += [state['messages'][-1]]
    
    return state | {"messages": [new_output]}

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
        print(msg.content)
        return "generer_reponse"