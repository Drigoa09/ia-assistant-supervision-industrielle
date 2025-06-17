from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLineEdit, QPushButton, QHBoxLayout, QApplication
import markdown2


# Vue de la fenêtre de chat
class ChatWindow(QWidget):
    # Constructeur de la fenêtre de chat
    def __init__(self, controller):
        super().__init__() # Appel du constructeur de QWidget
        self.setWindowTitle("Assistant Industriel 🤖") # Titre de la fenêtre
        self.setMinimumSize(600, 500) # Taille minimale de la fenêtre
        self.controller = controller # Stockage du contrôleur

        self.layout = QVBoxLayout() # Création du layout vertical
        self.setLayout(self.layout) # Application du layout à la fenêtre

        self.chat_display = QTextEdit() # Zone d'affichage du chat
        self.chat_display.setReadOnly(True) # Rendre la zone d'affichage en lecture seule
        self.layout.addWidget(self.chat_display) # Ajout de la zone d'affichage au layout

        input_layout = QHBoxLayout() # Création du layout horizontal pour les entrées
        self.input_field = QLineEdit() # Champ de saisie pour l'utilisateur
        self.input_field.setPlaceholderText("Posez votre question ici...") # Texte d'instruction
         # Bouton d'envoi
        self.send_button = QPushButton("Envoyer")
        self.send_button.setToolTip("Envoyer votre question")
        # Bouton pour quitter l'application
        self.quit_button = QPushButton("Quitter")
        self.quit_button.setToolTip("Quitter l'application")

        # Ajout du champ de saisie et du bouton au layout horizontal
        input_layout.addWidget(self.input_field)
        input_layout.addWidget(self.send_button)
        input_layout.addWidget(self.quit_button)
        self.layout.addLayout(input_layout)
        
        self.send_button.clicked.connect(self.controller.on_send_clicked) # Connexion du bouton d'envoi à la méthode du contrôleur
        self.input_field.returnPressed.connect(self.controller.on_send_clicked) # Connexion de la touche "Entrée" à la méthode du contrôleur
        self.quit_button.clicked.connect(QApplication.instance().quit) # Connexion du bouton de quitter à l'application
    # Fonction pour ajouter un message à la zone d'affichage du chat
    def append_message(self, sender, content):
        self.chat_display.append(f"<b>{sender}:</b> {content}")
    # Fonction pour afficher un message de chargement
    def show_loading(self):
        self.append_message("Assistant", "... en train de réfléchir 🤔")
        self.chat_display.repaint()
        QApplication.processEvents()
        self.input_field.clear()
    # Fonction pour masquer le message de chargement
    def hide_loading(self):
        self.chat_display.repaint()
        QApplication.processEvents()
        self.input_field.clear()
    # Fonction pour afficher la réponse de l'assistant
    def display_response(self, markdown_text):
        html = markdown2.markdown(markdown_text)
        self.chat_display.append(f"<b>Assistant:</b><br>{html}")
