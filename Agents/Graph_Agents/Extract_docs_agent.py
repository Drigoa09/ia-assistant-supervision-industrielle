from typing import Literal
from langchain_core.messages.ai import AIMessage
from OrderState import OrderState
from model import model

from Tools_nodes.database_node import llm_with_tools

AGENT_GENERATION_SYSINT = (
    '''
Tu es un agent interprète spécialisé dans l’industrie.

Tu essaies de répondre aux questions avec les outils qui te sont donnés, pas à pas. 
''')

exemple1 = (''' Question
Musician and satirist Allie Goertz wrote a song about the "The Simpsons" character Milhouse, who Matt Groening named after who?

Thought 1
The question simplifies to "The Simpsons" character Milhouse is named after who. I only need to search Milhouse and find who it is named after.

Action 1
Use tools''')

exemple2 = ('''
Observation 1
Milhouse Mussolini Van Houten is a recurring character in the Fox animated television series The Simpsons voiced by Pamela Hayden and created by Matt Groening.

Thought 2
The paragraph does not tell who Milhouse is named after, maybe I can look up "named after".

Action 2
Use tools.'''

)

from langchain.agents import Tool, initialize_agent, AgentType
from Tools_nodes.database_node import tools

def extract_docs_agent(state: OrderState) -> OrderState:
    """The chatbot itself. A wrapper around the model's own chat interface."""
    agent = initialize_agent(
    tools=tools,
    llm=model,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    )
    new_output = agent.run([AGENT_GENERATION_SYSINT] + state["messages"])

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
        return "generer_reponse"