from typing import Literal
from State import State

from langchain_core.messages import HumanMessage

from langgraph.graph import END

import matplotlib.pyplot as plt

from interface import interface_view

import matplotlib.pyplot as plt
import matplotlib.animation as animation

from datetime import datetime

from langchain_core.messages.ai import AIMessage

WELCOME_MSG = "Bonjour ! Je suis votre assistant, comment puis-je vous aider?"

class Human:

    def __init__(self, name : str, welcome_msg : str):
        self.name = name
        self.welcome_msg = welcome_msg
    
    def demander_question(self, state : State) -> State:
        '''
        if state["dataFrames"]:
            dataSent = state["dataFrames"][0]["dataFrame"].groupby("sigscan_object_name").apply(lambda x: x.drop(columns="sigscan_object_name").to_dict(orient="records")).to_dict()
            request = state['call_request']

            self.interface_view = interface_view(dataSent)

            start_temps = request.startDate
            if start_temps != None:
                start = datetime(start_temps.annee, start_temps.mois, start_temps.jour).timestamp()
            else:
                start = datetime.now().timestamp() - 7.776 * 10**6
            
            end_temps = request.startDate
            if end_temps != None:
                end = datetime(end_temps.annee, end_temps.mois, end_temps.jour).timestamp()
            else:
                end = datetime.now().timestamp()

            self.interface_view.set_caracs(start, end, 10000)
            ani = animation.FuncAnimation(fig=self.interface_view.fig, func=self.interface_view.animate, frames=10000, interval=1)
            
            plt.show()
        '''

        if not state["messages"]:
            # Premier tour : injecter le message de bienvenue
            state["messages"].append(AIMessage(content=WELCOME_MSG))
            state["finished"] = True  # Stopper pour éviter de re-boucler
            return state
    
        #Calcul des tokens

        last_msg = state["messages"][-1]

        if isinstance(last_msg, AIMessage):
            state["finished"] = True
        elif isinstance(last_msg, HumanMessage):
            print("[Utilisateur]:", last_msg.content)
            state["question"] = last_msg.content

        return state

        if state['messages']:
            print("Model : " + state['messages'][-1].content)
        else:
            print(self.welcome_msg)

        content = input(self.name + " : ")

        if content in {"q", "quit", "exit", "goodbye"}:
            state["finished"] = True
        state["question"] = content

        return state | {"messages" : [HumanMessage(content)]}

    def maybe_exit_with_human_node(self, state : State) -> Literal["Formalisateur de requête", "__end__"]:
        if state['finished']:
            return END
        else:
            return "Formalisateur de requête"
