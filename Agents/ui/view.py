from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLineEdit, QPushButton, QHBoxLayout, QApplication, QLabel, QSpacerItem, QSizePolicy, QScrollArea, QGraphicsOpacityEffect
import markdown2
from ui.CollapsibleBox import CollapsibleBox 
from PySide6.QtCore import Qt, QTimer, QSize, QPropertyAnimation
from PySide6.QtGui import QMovie
import os
from PySide6.QtCore import Slot
from langchain_core.messages import AIMessage
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
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
        self.chat_display.setStyleSheet("""
            QTextEdit {
                background-color: #fefefe;
                font-family: Consolas, monospace;
                font-size: 13px;
                padding: 8px;
                border: 1px solid #ccc;
                border-radius: 5px;
            }
        """)
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
        # --- Chargement GIF + Texte ---
        gif_path = os.path.join(os.path.dirname(__file__), "assets", "thinking-ezgif.com-crop.gif")
        self.loading_movie = QMovie(gif_path)
        self.loading_movie.setScaledSize(QSize(24, 24))

        self.loading_gif_label = QLabel()
        self.loading_gif_label.setMovie(self.loading_movie)
        self.loading_gif_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.loading_gif_label.setStyleSheet("margin: 0px; padding: 0px;")

        self.loading_text_label = QLabel("Réflexion en cours…")
        self.loading_text_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.loading_text_label.setStyleSheet("margin: 0px; padding: 0px;")

        # 📦 Layout horizontal avec un spacer à droite pour pousser les widgets à gauche
        self.loading_layout = QHBoxLayout()
        self.loading_layout.setContentsMargins(0, 0, 0, 0)
        self.loading_layout.setSpacing(0)
        self.loading_layout.addWidget(self.loading_gif_label)
        self.loading_layout.addWidget(self.loading_text_label)
        
        

        # 🧱 Ajout du spacer à droite
        spacer = QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.loading_layout.addItem(spacer)

        self.loading_widget = QWidget()
        self.loading_widget.setLayout(self.loading_layout)
        self.loading_widget.setVisible(False)  # Caché par défaut

        # N'oublie pas de l’ajouter au layout principal
        self.layout.addWidget(self.loading_widget)
        
        # Ajout du champ de saisie et du bouton au layout horizontal
        input_layout.addWidget(self.input_field)
        input_layout.addWidget(self.send_button)
        input_layout.addWidget(self.quit_button)
        self.layout.addLayout(input_layout)
        
        self.send_button.clicked.connect(self.controller.on_send_clicked) # Connexion du bouton d'envoi à la méthode du contrôleur
        self.input_field.returnPressed.connect(self.controller.on_send_clicked) # Connexion de la touche "Entrée" à la méthode du contrôleur
        self.quit_button.clicked.connect(QApplication.instance().quit) # Connexion du bouton de quitter à l'application
        self.summary_box = None  # 🔥 pour mémoriser la box actuelle
        self.fade_animation = None

        self.append_collapsible_summary("<b>Résumé de test</b>")
        self.dots_timer = QTimer()
        self.dots_timer.timeout.connect(self._animate_loading_text)
        self.dots_state = 0
        #self.show_loading()
        #QTimer.singleShot(3000, self.hide_loading)  # Cache l'animation après 3s


    # Fonction pour ajouter un message à la zone d'affichage du chat
    def append_message(self, sender, content):
        self.chat_display.append(f"<b>{sender}:</b> {content}")
        self.chat_display.verticalScrollBar().setValue(self.chat_display.verticalScrollBar().maximum())
    # Fonction pour afficher un message de chargement
    def show_loading(self):
        self.dots_state = 0
        self.loading_text_label.setText("Réflexion en cours")
        self.loading_widget.setVisible(True)
        self.loading_movie.start()
        self.dots_timer.start(500)  # Rafraîchissement toutes les 500ms
        QApplication.processEvents()
    # Fonction pour cacher le message de chargement
    def hide_loading(self):
        self.dots_timer.stop()
        self.loading_movie.stop()
        self.loading_widget.setVisible(False)
        QApplication.processEvents()
    # Fonction pour animer le texte de chargement
    def _animate_loading_text(self):
        dots = '.' * (self.dots_state % 4)  # "", ".", "..", "..."
        self.loading_text_label.setText(f"Réflexion en cours{dots}")
        self.dots_state += 1
    # Fonction pour afficher la réponse de l'assistant
    def display_response(self, markdown_text):
        html = markdown2.markdown(markdown_text)
        self.chat_display.append(f"<b>Assistant:</b><br>{html}")
    # Fonction pour le résumé 
    def append_collapsible_summary(self, html_summary: str):
        if self.summary_box is None:
            self.summary_box = CollapsibleBox("📊 Résumé")

            # Contenu scrollable
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setMinimumHeight(10)  #  ajustable selon ton besoin
            scroll.setStyleSheet("QScrollArea { border: none; }")  # clean look

            label = QLabel()
            label.setTextFormat(Qt.TextFormat.RichText)
            label.setWordWrap(True)
            label.setTextInteractionFlags(Qt.TextSelectableByMouse)  # optionnel : permet de copier
            label.setText(html_summary)

            scroll.setWidget(label)

            self.summary_box.setContent(scroll)
            self.layout.insertWidget(self.layout.count() - 2, self.summary_box)
        else:
            scroll = self.summary_box.content_area.layout().itemAt(0).widget()
            label = scroll.widget()
            label.setText(html_summary)
        self.summary_box.content_area.setVisible(True)
        self.summary_box.toggle_button.setChecked(True)
        self.summary_box.toggle_button.setArrowType(Qt.DownArrow)
    def set_controller(self, controller):
        self.controller = controller  # accès au contrôleur depuis la vue
    def append_matplotlib_plot(self, fig):
        canvas = FigureCanvas(fig)
        canvas.setMinimumHeight(300)  # Tu peux ajuster

        # Option simple sans box repliable:
        #self.layout.insertWidget(self.layout.count() - 2, canvas)

        # dans une box repliable
        scroll_area = QScrollArea()
        scroll_area.setWidget(canvas)
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        box = CollapsibleBox("📈 Graphique généré")
        box.setContent(scroll_area)
        self.layout.insertWidget(self.layout.count() - 2, box)
    @Slot()
    def update_after_response(self):
        try:
            summary = self.controller._format_summary(self.controller.state)
            self.append_collapsible_summary(summary)
        except Exception as e:
            print("Erreur dans le résumé:", e)

        last = self.controller.history[-1]
        if isinstance(last, AIMessage):
            self.display_response(last.content)

        # 🎯 Affiche le graphique si présent
        fig = self.controller.state.get("figure")
        if fig:
            self.append_matplotlib_plot(fig)

        self.hide_loading()

    @Slot(str)
    def display_error(self, error_msg):
        self.append_message("Erreur", error_msg)
        self.hide_loading()
