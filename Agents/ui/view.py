from PySide6.QtWidgets import QWidget, QVBoxLayout, QFrame, QTextBrowser, QLineEdit, QPushButton, QHBoxLayout, QApplication, QFileDialog, QLabel, QSpacerItem, QSizePolicy, QScrollArea, QGraphicsOpacityEffect, QGraphicsDropShadowEffect
import markdown2
from ui.CollapsibleBox import CollapsibleBox 
from PySide6.QtCore import Qt, QTimer, QSize, QPropertyAnimation, QParallelAnimationGroup, QEasingCurve
from PySide6.QtGui import QMovie, QPixmap
import os
from PySide6.QtCore import Slot
from langchain_core.messages import AIMessage
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

# Vue de la fenêtre de chat
class ChatWindow(QWidget):
    # Constructeur de la fenêtre de chat
    def __init__(self, controller):
        super().__init__() # Appel du constructeur de QWidget
        self._active_animations = []
        self.setWindowTitle("Assistant Industriel 🤖") # Titre de la fenêtre
        self.setMinimumSize(600, 500) # Taille minimale de la fenêtre
        self.controller = controller # Stockage du contrôleur

        self.layout = QVBoxLayout() # Création du layout vertical
        self.setLayout(self.layout) # Application du layout à la fenêtre
        # Layout des boutons "Exporter" et "Charger"
        action_layout = QHBoxLayout()
        self.save_button = QPushButton("📥 Exporter le chat")
        self.load_button = QPushButton("📂 Charger l'historique")
        self.save_button.clicked.connect(lambda: self.controller.save_history_to_file())
        self.load_button.clicked.connect(lambda: self.controller.open_history_file_dialog())

        action_layout.addWidget(self.save_button)
        action_layout.addWidget(self.load_button)

        self.layout.addLayout(action_layout)  # ➕ tout en haut
        self.chat_scroll = QScrollArea()
        self.chat_scroll.setWidgetResizable(True)
        self.chat_scroll.setStyleSheet("QScrollArea { background: #fefefe; border: 1px solid #ccc; border-radius: 5px; }")

        self.chat_container = QWidget()
        self.chat_layout = QVBoxLayout()
        self.chat_layout.setAlignment(Qt.AlignTop)  # 🔥 aligne en haut
        self.chat_container.setLayout(self.chat_layout)

        self.chat_scroll.setWidget(self.chat_container)
        self.layout.addWidget(self.chat_scroll)

        #self.chat_display = QTextEdit() # Zone d'affichage du chat
        #self.chat_display.setReadOnly(True) # Rendre la zone d'affichage en lecture seule

        #self.layout.addWidget(self.chat_display) # Ajout de la zone d'affichage au layout

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

        #self.append_collapsible_summary("<b>Résumé de test</b>")
        self.dots_timer = QTimer()
        self.dots_timer.timeout.connect(self._animate_loading_text)
        self.dots_state = 0
        style = """
        /* Bouton générique */
        QPushButton {
            border: none;
            padding: 8px 14px;
            border-radius: 6px;
            font-size: 14px;
            font-weight: bold;
            min-width: 90px;
        }

        /* Effet hover (zoom) */
        QPushButton:hover {
            padding: 9px 15px;
        }

        /* Bouton Envoyer (Bleu) */
        QPushButton#send_button {
            background-color: #2196F3;
            color: white;
        }
        QPushButton#send_button:hover {
            background-color: #1976D2;
        }
        QPushButton#send_button:pressed {
            background-color: #0D47A1;
        }

        /* Bouton Quitter (Rouge) */
        QPushButton#quit_button {
            background-color: #f44336;
            color: white;
        }
        QPushButton#quit_button:hover {
            background-color: #d32f2f;
        }
        QPushButton#quit_button:pressed {
            background-color: #b71c1c;
        }

        /* Boutons du haut (Gris/bleu clair) */
        QPushButton#load_button,
        QPushButton#save_button,
        summary_box.toggle_button {
            background-color: #e0e0e0;
            color: #333;
        }
        QPushButton#load_button:hover,
        QPushButton#save_button:hover {
            background-color: #bdbdbd;
        }
        QPushButton#load_button:pressed,
        QPushButton#save_button:pressed {
            background-color: #9e9e9e;
        }
        """
        self.input_field.setStyleSheet("""
            QLineEdit {
                padding: 8px 12px;
                border: 2px solid #ccc;
                border-radius: 6px;
                font-size: 14px;
                background-color: #ffffff;
                color: #333;
            }

            QLineEdit:focus {
                border: 2px solid #2196F3;
                background-color: #f0f8ff;
            }
        """)
        for btn in [self.send_button, self.quit_button, self.save_button, self.load_button]:
            btn.setCursor(Qt.PointingHandCursor)

        self.setStyleSheet(style)

        self.send_button.setObjectName("send_button")
        self.quit_button.setObjectName("quit_button")
        self.load_button.setObjectName("load_button")
        self.save_button.setObjectName("save_button")

        #self.show_loading()
        #QTimer.singleShot(3000, self.hide_loading)  # Cache l'animation après 3s

    def _open_history_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Charger un historique", "", "Fichiers JSON (*.json)")
        if file_path:
            self.controller.load_history_from_file(file_path)
    def fade_in_widget(self, widget, duration=800):
        widget.setVisible(True) 
        effect = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(effect)

        animation = QPropertyAnimation(effect, b"opacity", widget)
        animation.setDuration(duration)
        animation.setStartValue(0.0)
        animation.setEndValue(1.0)
        animation.start()

        # 🔐 Stockage fort (pas juste une propriété du widget) pour éviter la suppression
        self._active_animations.append(animation)

        # 🔁 Nettoyage automatique une fois l'animation terminée
        animation.finished.connect(lambda: self._active_animations.remove(animation))


    def _slide_and_fade_in(self, widget, duration=800):
        #widget.setVisible(True)
        widget.adjustSize()  # 🔧 important pour bien récupérer sizeHint()

        full_height = widget.sizeHint().height()

        effect = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(effect)

        fade = QPropertyAnimation(effect, b"opacity", widget)
        fade.setDuration(duration)
        fade.setStartValue(0.0)
        fade.setEndValue(1.0)

        widget.setMaximumHeight(0)  # 🧨 réduit à 0 pour slider depuis rien

        slide = QPropertyAnimation(widget, b"maximumHeight", widget)
        slide.setDuration(duration)
        slide.setStartValue(0)
        slide.setEndValue(full_height)
        slide.setEasingCurve(QEasingCurve.OutCubic)

        group = QParallelAnimationGroup()
        group.addAnimation(fade)
        group.addAnimation(slide)

        # 🔐 Sauvegarde pour ne pas garbage collect l’anim
        if not hasattr(self, "_active_animations"):
            self._active_animations = []
        self._active_animations.append(group)

        def _on_finished():
            widget.setMaximumHeight(16777215)  # 🔓 Qt max height
            self._active_animations.remove(group)

        group.finished.connect(_on_finished)
        group.start()
    def _create_chat_bubble(self, icon_path, html_text):

        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)

        # 🖼️ Icône à gauche
        icon_label = QLabel()
        icon_pixmap = QPixmap(icon_path)
        if not icon_pixmap.isNull():
            icon_label.setPixmap(icon_pixmap.scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        icon_label.setFixedSize(36, 36)
        icon_label.setStyleSheet("background-color: #E0F7FA; border-radius: 6px; padding: 2px;")
        layout.addWidget(icon_label)

        # 🗨️ Bulle de texte
        bubble = QLabel(html_text)
        bubble.setTextFormat(Qt.TextFormat.RichText)
        bubble.setWordWrap(True)
        bubble.setTextInteractionFlags(Qt.TextSelectableByMouse)  # texte sélectionnable
        bubble.setStyleSheet("""
            QLabel {
                background-color: #FFFFFF;
                border-radius: 8px;
                padding: 8px;
                font-size: 13px;
            }
        """)
        bubble.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        layout.addWidget(bubble, 1)

        return container



    # Fonction pour ajouter un message à la zone d'affichage du chat
    def append_message(self, sender, content):
        user_icon = os.path.join(os.path.dirname(__file__), "assets", "user_icon.png")
        bubble = self._create_chat_bubble(user_icon, f"<b>{sender}:</b> {content}")
        self.chat_layout.addWidget(bubble)
        self.fade_in_widget(bubble)
        QTimer.singleShot(100, lambda: self.chat_scroll.verticalScrollBar().setValue(
            self.chat_scroll.verticalScrollBar().maximum()))

    """ def append_message(self, sender, content):
        label = QLabel(f"<b>{sender}:</b> {content}")
        label.setTextFormat(Qt.TextFormat.RichText)
        label.setWordWrap(True)
        label.setStyleSheet("padding: 6px;")
        self.chat_layout.addWidget(label)

        self.fade_in_widget(label)
        QTimer.singleShot(100, lambda: self.chat_scroll.verticalScrollBar().setValue(
            self.chat_scroll.verticalScrollBar().maximum())) """

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

        # 🔎 Vérifie si c'est du HTML complexe (tableau, div, etc.)
        if "<table" in html or "<div" in html:
            browser = QTextBrowser()
            browser.setHtml(f"<b>Assistant:</b><br>{html}")
            browser.setOpenExternalLinks(True)
            browser.setStyleSheet("""
                QTextBrowser {
                    background-color: #1e1e1e;
                    color: white;
                    border: none;
                    padding: 6px;
                    border-radius: 6px;
                }
            """)
            content_widget = browser
        else:
            label = QLabel(f"<b>Assistant:</b> {html}")
            label.setTextFormat(Qt.TextFormat.RichText)
            label.setWordWrap(True)
            label.setStyleSheet("padding: 6px;")
            content_widget = label

        # 💬 Crée une bulle avec icône
        icon_path = os.path.join(os.path.dirname(__file__), "assets", "robot_icon.png")
        bubble = self._create_chat_bubble(icon_path, f"<b>Assistant:</b> {html}")
        self.chat_layout.addWidget(bubble)
        self.fade_in_widget(bubble)

        # ⬇️ Scroll vers le bas
        QTimer.singleShot(100, lambda: self.chat_scroll.verticalScrollBar().setValue(
            self.chat_scroll.verticalScrollBar().maximum()))
    # Fonction pour le résumé 
    def append_collapsible_summary(self, html_summary: str):
        if self.summary_box is None:
            self.summary_box = CollapsibleBox("📊 Résumé")

            label = QLabel()
            label.setTextFormat(Qt.TextFormat.RichText)
            label.setWordWrap(True)
            label.setTextInteractionFlags(Qt.TextSelectableByMouse)
            label.setText(html_summary)

            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setStyleSheet("QScrollArea { border: none; }")
            scroll.setWidget(label)

            # ⬇️ Emballage dans un frame (fixe le problème de layout durant l’anim)
            wrapper = QFrame()
            layout = QVBoxLayout()
            layout.setContentsMargins(0, 0, 0, 0)
            layout.addWidget(scroll)
            wrapper.setLayout(layout)

            self.summary_box.setContent(wrapper)
            self.layout.insertWidget(self.layout.count() - 2, self.summary_box)

            QTimer.singleShot(0, lambda: self._slide_and_fade_in(self.summary_box))  # ⬅️ Animation ici
        else:
            scroll = self.summary_box.content_area.layout().itemAt(0).widget().layout().itemAt(0).widget()
            label = scroll.widget()
            label.setText(html_summary)

        self.summary_box.content_area.setVisible(True)
        self.summary_box.toggle_button.setChecked(True)
        self.summary_box.toggle_button.setArrowType(Qt.DownArrow)

    def set_controller(self, controller):
        self.controller = controller  # accès au contrôleur depuis la vue

    def showEvent(self, event):
        super().showEvent(event)

        # Appelle une fonction d’accueil une seule fois
        if not hasattr(self, "_welcome_done"):
            self.controller.display_welcome_message()
            self._welcome_done = True

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

        # 🎯 Affiche le graphique si présent
        fig = self.controller.state.get("figure")
        if fig:
            self.display_response("📈 Voici le graphique généré à partir des données sélectionnées.")
            self.append_matplotlib_plot(fig)
        else:
            # S’il n’y a pas de figure, affiche le message AI normal
            last = self.controller.history[-1]
            if isinstance(last, AIMessage):
                self.display_response(last.content)

        self.hide_loading()


    @Slot(str)
    def display_error(self, error_msg):
        self.append_message("Erreur", error_msg)
        self.hide_loading()
