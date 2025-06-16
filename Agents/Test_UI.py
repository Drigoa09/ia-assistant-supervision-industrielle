import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QTextEdit, QLineEdit, QPushButton, QLabel, QHBoxLayout
)
from PySide6.QtCore import Qt

from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from index import chat_with_human_graph
from OrderState import OrderState
import markdown2
import os
from dotenv import load_dotenv
load_dotenv()
# Vérification de la présence des variables essentielles
missing = [var for var in ["ES_HOST", "ES_USER", "ES_PASSWORD"] if not os.getenv(var)]
if missing:
    print(f"❌ Erreur : Les variables suivantes sont manquantes dans .env : {', '.join(missing)}")
    sys.exit(1)
class ChatWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Assistant Industriel Local 🤖")
        self.setMinimumSize(600, 500)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.layout.addWidget(self.chat_display)

        input_layout = QHBoxLayout()
        self.input_field = QLineEdit()
        self.send_button = QPushButton("Envoyer")
        input_layout.addWidget(self.input_field)
        input_layout.addWidget(self.send_button)
        self.layout.addLayout(input_layout)

        self.send_button.clicked.connect(self.send_message)
        self.input_field.returnPressed.connect(self.send_message)

        self.history = []  # Historique des messages
        self.append_message("Assistant", "Bonjour 👋 ! Je suis votre assistant industriel. Posez-moi une question.")
    def append_message(self, sender, content):
        self.chat_display.append(f"<b>{sender}:</b> {content}")

    def has_unanswered_tool(self, history):
        for msg in reversed(history):
            if isinstance(msg, AIMessage):
                return False
            if isinstance(msg, ToolMessage):
                return True
        return False

    def send_message(self):
        # 👮 Sécurité stricte : si le dernier message est AI, on bloque
        while self.history and (isinstance(self.history[-1], AIMessage) or self.has_unanswered_tool(self.history)):
            self.history.pop()  # Retirer le dernier message AI/ToolMessage pour éviter la boucle infinie
        user_text = self.input_field.text().strip()
        if not user_text:
            return

        self.append_message("Vous", user_text)
        self.input_field.clear()

        loading_label = "Assistant"
        loading_message = "... en train de réfléchir 🤔"
        self.append_message(loading_label, loading_message)
        self.chat_display.repaint()
        QApplication.processEvents()
        self.input_field.clear()
        last_human_index = max((i for i, m in enumerate(self.history) if isinstance(m, HumanMessage)), default=-1)
        self.history = self.history[:last_human_index + 1]
        # Ajouter le message utilisateur à l’historique global
        self.history.append(HumanMessage(content=user_text))
        clean_messages = list(self.history)
        """ # Créer un état propre, SANS laisser d'AIMessage en dernier
        

        # ✅ Si le dernier est un AIMessage, on le retire pour éviter l'erreur
        while clean_messages and isinstance(clean_messages[-1], AIMessage):
            clean_messages.pop()
 """
        """ # Si le dernier message est un ToolMessage, on ne peut pas ajouter un HumanMessage ensuite
        if clean_messages and isinstance(clean_messages[-1], ToolMessage):
            self.append_message("Erreur", "L'agent a récemment utilisé un outil. Impossible d'ajouter une nouvelle requête humaine sans réponse du modèle.")
            return """
        # Ajout du nouveau message utilisateur
        clean_messages.append(HumanMessage(content=user_text))
        state = {
            "messages": clean_messages,
            "order": [],
            "question": [],
            "tools_to_answer": [],
            "finished": False,
            "Trois": False
        }

        try:
            result = chat_with_human_graph.invoke(state, config={"recursion_limit": 100})
            new_messages = result.get("messages", [])
            self.chat_display.undo()
            # Trouver les réponses de l’assistant ajoutées après ce message
            # Regrouper tous les AIMessage après le dernier HumanMessage
            last_user_idx = max(i for i, m in enumerate(new_messages) if isinstance(m, HumanMessage))
            assistant_responses = [
                msg.content for msg in new_messages[last_user_idx + 1:]
                if isinstance(msg, AIMessage)
            ]

            if assistant_responses:
                full_response = "\n".join(assistant_responses).strip()
                #self.append_message("Assistant", full_response)
                # réponse markdown2 html
                html_content = markdown2.markdown(full_response)
                self.chat_display.append(f"<b>Assistant:</b><br>{html_content}")
            # Mettre à jour tout l'historique pour le prochain tour
            self.history = new_messages

        except Exception as e:
            self.append_message("Erreur", str(e))



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ChatWindow()
    window.show()
    sys.exit(app.exec())
