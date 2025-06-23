from PySide6.QtWidgets import QGroupBox, QVBoxLayout, QToolButton, QWidget, QSizePolicy
from PySide6.QtCore import Qt


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

        layout = QVBoxLayout()
        layout.addWidget(self.toggle_button)
        layout.addWidget(self.content_area)
        self.setLayout(layout)

    def toggle_content(self):
        visible = not self.content_area.isVisible()
        self.content_area.setVisible(visible)
        self.toggle_button.setArrowType(Qt.DownArrow if visible else Qt.RightArrow)
        self.adjustSize()

    def setContent(self, content_widget):
        content_layout = QVBoxLayout()
        content_layout.addWidget(content_widget)
        self.content_area.setLayout(content_layout)
