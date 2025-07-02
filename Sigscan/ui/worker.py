from PySide6.QtCore import QObject, Signal
from langchain_core.messages import HumanMessage
from index import chat_with_human_graph

class Worker(QObject):
    finished = Signal(object, object)  # history, state
    error = Signal(str)

    def __init__(self, history, user_text):
        super().__init__()
        self.history = history
        self.user_text = user_text

    def run(self):
        try:
            messages = list(self.history) + [HumanMessage(content=self.user_text)]
            state = {
                "messages": messages,
                "order": [],
                "question": [],
                "tools_to_answer": [],
                "finished": False,
                "Trois": False,
                "request_call": None,  # Assurez-vous que request_call est initialisé
                "request_call_initial": None,  # Assurez-vous que request_call_initial est initialisé
                "traitement_format": None,  # Assurez-vous que traitement_format est initialisé
                "dataFrames": [],  # Assurez-vous que dataFrames est initialisé
                "input_tokens" : 0,
                "output_tokens" : 0
            }
            result = chat_with_human_graph.invoke(state, config={"recursion_limit": 100})
            new_history = result["messages"]
            
            # ✅ Astuce sécurité : pas d’objet Qt dans le state retourné
            state_copy = dict(result)
            self.finished.emit(new_history, state_copy)
        except Exception as e:
            self.error.emit(str(e))
