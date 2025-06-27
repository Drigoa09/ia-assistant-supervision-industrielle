from typing import Literal
from State import State

from langchain_core.messages import HumanMessage

from langgraph.graph import END

class Human:

    def __init__(self, name : str, welcome_msg : str):
        self.name = name
        self.welcome_msg = welcome_msg
    
    def demander_question(self, state : State) -> State:
        if state['messages']:
            print("Model : " + state['messages'][-1].content)
        else:
            print(self.welcome_msg)

        content = input(self.name + " : ")

        if content in {"q", "quit", "exit", "goodbye"}:
            state["finished"] = True

        return state | {"messages" : [HumanMessage(content)]}

    def maybe_exit_with_human_node(self, state : State) -> Literal["Formalisateur de requête", "__end__"]:
        if state['finished']:
            return END
        else:
            return "Formalisateur de requête"
