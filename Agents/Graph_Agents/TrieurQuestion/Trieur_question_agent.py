from typing import List
from pydantic import BaseModel, Field
from typing import Optional, List
from OrderState import OrderState
from model import model_codestral, model_mistral_medium
from Graph_Agents.TrieurQuestion.Trieur_prompt import AGENT_JOB

from Graph_Agents.Agent import Agent
from langchain_core.messages import HumanMessage, AIMessage

from datetime import datetime
class Trieur_question_agent(Agent):
    "Agent responsible for processing if the question is related to Sigscan or HURON"

    def __init__(self, OutputSchema):
        self.structured_llm = model_mistral_medium.with_structured_output(OutputSchema, include_raw=True)

    def interaction(self, state: OrderState) -> OrderState:
        new_output = self.structured_llm.invoke([AGENT_JOB, state['question']])
        print(f"Réponse brute : {new_output}")
        state['input_tokens'], state['output_tokens'] = self.obtenir_tokens(new_output['raw'])
        state['prix_input_tokens'] += state['input_tokens'] * 0.4 / 10 ** 6
        state['prix_output_tokens'] += state['output_tokens'] * 2 / 10 ** 6

        parsed = new_output.get('parsed')
        if parsed is not None and hasattr(parsed, 'result'):
            val = parsed.result
            if val == None:
                state['Huron_related'] = None
                state['messages'].append(AIMessage(content = "Réponse incomprise"))
            elif val:
                state['Huron_related'] = True
            elif not val:
                state['Huron_related'] = False
                #None
            print(f"✅ Question en relation avec Huron : {state['Huron_related']}")
        else:
            raise ValueError("❌ Parsing échoué : pas de champ 'result' dans la sortie.")

        print(f"Question en relation avec Huron : {state['Huron_related']}\n")
        return state