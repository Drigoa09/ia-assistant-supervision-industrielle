from PySide6.QtWidgets import QGroupBox, QVBoxLayout, QToolButton, QWidget, QSizePolicy
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve


class CollapsibleBox(QGroupBox):
    def __init__(self, title="", parent=None):
        super().__init__(parent)
        self.toggle_button = QToolButton()
        self.toggle_button.setText(title)
        self.toggle_button.setCheckable(True)
        self.toggle_button.setChecked(False)
        self.toggle_button.setArrowType(Qt.RightArrow)  # 🔼 flèche initiale
        self.toggle_button.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.toggle_button.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)  # ⬅️ largeur minimale
        self.toggle_button.clicked.connect(self.toggle_content)

        self.content_area = QWidget()
        self.content_area.setVisible(False)
        self.content_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.content_area.setMaximumHeight(0)  # 🔥 important pour anim correcte
        self.toggle_button.setStyleSheet("""
            QToolButton {
                background-color: #E3F2FD;
                border: 1px solid #90CAF9;
                border-radius: 6px;
                padding: 6px 12px;
                font-weight: bold;
                color: #1565C0;
                text-align: left;
            }
            QToolButton:hover {
                background-color: #BBDEFB;
            }
            QToolButton:pressed {
                background-color: #90CAF9;
            }
        """)
        

        layout = QVBoxLayout()
        layout.addWidget(self.toggle_button)
        layout.addWidget(self.content_area)
        self.setLayout(layout)

    def toggle_content(self):
        expanded = self.content_area.isVisible()
        direction = not expanded  # True si on va ouvrir

        self.toggle_button.setArrowType(Qt.DownArrow if direction else Qt.RightArrow)

        if direction:
            self.content_area.setVisible(True)
            self.content_area.adjustSize()
            target_height = self.content_area.sizeHint().height()
        else:
            target_height = 0

        self.animation = QPropertyAnimation(self.content_area, b"maximumHeight")
        self.animation.setDuration(300)
        self.animation.setStartValue(self.content_area.height())
        self.animation.setEndValue(target_height)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        self.animation.start()

        if not direction:
            # Cache le widget à la fin de l’animation
            self.animation.finished.connect(lambda: self.content_area.setVisible(False))

    def setContent(self, content_widget):
        content_layout = QVBoxLayout()
        content_layout.addWidget(content_widget)
        self.content_area.setLayout(content_layout)
