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

from Tools_nodes.treatment_tools.traitement_format import Traitement_Format

structured_llm = model_codestral.with_structured_output(Traitement_Format)

def treatment_agent(state: OrderState) -> OrderState:
    """The chatbot itself. A wrapper around the model's own chat interface."""

    if state['traitement'] != None:
        AGENT_GENERATION_SYSINT = '''
        Tu es un agent interprète spécialisé dans l’industrie.

        Tu essaies de répondre aux questions avec les outils qui te sont donnés, pas à pas.
        Tu as accès aux clés de dataFrame : \n
        '''
        n = len(state['dataFrames_columns'])
        
        for i in range(n):
            AGENT_GENERATION_SYSINT +=  state['dataFrames_columns'][i] + " : " + state['dataFrames_role'][i] + "\n"

        state['request_call'] = structured_llm.invoke([AGENT_GENERATION_SYSINT, state['traitement']])

        print(state['request_call'])

    return state