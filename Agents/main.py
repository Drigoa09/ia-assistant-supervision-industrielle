import sys
from PySide6.QtWidgets import QApplication
from ui.view import ChatWindow
from ui.controller import ChatController

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    controller = ChatController()
    view = ChatWindow(controller)
    controller.view = view
    view.show()
    sys.exit(app.exec())
