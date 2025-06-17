from logic.core import process_user_input

class ChatController:
    def __init__(self):
        self.view = None
        self.history = []

    def set_view(self, view):
        self.view = view

    def on_send_clicked(self):
        user_text = self.view.input_field.text().strip()
        if not user_text:
            return
        # Clear the input field after getting the text
        self.view.input_field.clear()
        # Append the user message to the chat display
        self.view.append_message("Vous", user_text)
        self.view.show_loading()

        try:
            new_history = process_user_input(self.history, user_text)
            self.history = new_history
            assistant_responses = [
                m.content for m in new_history if m.type == "ai"
            ]
            if assistant_responses:
                self.view.display_response("\n".join(assistant_responses))
        except Exception as e:
            self.view.append_message("Erreur", str(e))
        finally:
            self.view.hide_loading()
