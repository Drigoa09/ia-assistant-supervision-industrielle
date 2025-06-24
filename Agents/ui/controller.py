from matplotlib import lines
from ui.view import CollapsibleBox, ChatWindow
from ui.worker import Worker
from PySide6.QtCore import QThread, QMetaObject, Qt, Q_ARG
#from langchain_core.messages import AIMessage
#from logic.core import process_user_input

class ChatController:
    def __init__(self):
        self.view = None
        self.history = []
        self.state = None  # 🆕 stocke le dernier état

    def set_view(self, view: ChatWindow):
        self.view = view
        self.view.set_controller(self)  # 🆕 (permet à la vue d'accéder au contrôleur)

    def _format_summary(self, state):
        print("📦 State keys: FORMAT_SUMMARY", list(state.keys()))
        req = state.get("request_call", None)
        fonctions = state.get("traitement_format", None)
        traitements = state.get("traitements", None)

        print("🔍 Résumé des traitements :", state.get("traitements",None))

        """ if not req:
            req = state.get("request_call") """
        print("🔍 Résumé de la requête (call) :", req)

        if not req:
            return "🤷 Je n’ai pas pu extraire la requête utilisateur."

        lines = [f"📋 <b>Résumé de la requête</b>"]

        # Infos générales
        lines.append(f"🧠 <b>Question</b> : {req.question_utilisateur}")
        lines.append(f"🎯 <b>Intention</b> : {req.intention}")
        lines.append(f"📂 <b>Type de traitement</b> : {req.type_traitement}")

        # Période + Machine + Variables
        if req.elements_cherches_request:
            el = req.elements_cherches_request[0]

            if el.periode_requete:
                date_from = el.periode_requete.date_from.split("T")[0]
                date_to = el.periode_requete.date_to.split("T")[0]
                lines.append(f"🗓️ <b>Période</b> : {date_from} → {date_to}")

            if el.machine_request:
                lines.append(f"🏭 <b>Machine</b> : {el.machine_request.name}")

            if el.variables_requete:
                lines.append("🔧 <b>Variables de la requête</b> :")
                for v in el.variables_requete:
                    lines.append(f"➡️ <b>{v.role}</b> : {v.alias}")

        # Résultat attendu
        if req.resultat_attendu:
            try:
                lines.append(f"📌 <b>Résultat attendu</b> : {', '.join(req.resultat_attendu)}")
            except TypeError:
                lines.append(f"📌 <b>Résultat attendu</b> : {req.resultat_attendu}")

        # Traitements effectués
        lines.append("🔧 <b>Traitements effectués</b> :")
        for i, t in enumerate(traitements):
            lines.append(f"➡️ Traitement {i + 1} : {t}")
        # Fonctions appelées
        lines.append("🛠️ <b>Fonctions appliquées :</b>")
        for i, f in enumerate(fonctions.fonctions_appelees):
            args_str = ', '.join(str(arg) for arg in f.args)  # Convertit tous les args en string
            lines.append(
                f"⚙️ <b>Fonction {i + 1}</b> : {f.fonction_appelee.value} avec args {args_str}"
            )

        return "<br>".join(lines)

    def on_send_clicked(self):
        user_text = self.view.input_field.text().strip()
        if not user_text:
            return
        self.view.input_field.clear()
        self.view.append_message("Vous", user_text)
        self.view.show_loading()

        self.thread = QThread()
        self.worker = Worker(self.history, user_text)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self._on_worker_finished)
        self.worker.error.connect(self._on_worker_error)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()
        """ try:
            result = process_user_input(self.history, user_text)
            self.history = result["messages"]
            try:
                summary = self._format_summary(result["state"])
                
                self.view.append_collapsible_summary(summary)
            except Exception as e:
                print("Erreur dans le résumé:", e)
            last_message = self.history[-1]
            if last_message.type == "ai":
                self.view.display_response(last_message.content)

        except Exception as e:
            self.view.append_message("Erreur", str(e))
        finally:
            self.view.hide_loading() """
    def _on_worker_finished(self, history, state):
        self.history = history
        self.state = state

        # 🧠 Appelle "update_after_response" sur la vue dans le bon thread
        QMetaObject.invokeMethod(self.view, "update_after_response")

    def _on_worker_error(self, error_msg):
        QMetaObject.invokeMethod(
            self.view,
            b"display_error",
            Qt.QueuedConnection,
            Q_ARG(str, error_msg)
        )

