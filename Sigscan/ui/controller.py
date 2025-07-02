from ui.view import ChatWindow
from ui.worker import Worker
from langchain_core.messages import AIMessage, HumanMessage
from PySide6.QtCore import QThread, QMetaObject, Qt, Q_ARG
from PySide6.QtWidgets import QFileDialog, QMessageBox
import json
from datetime import datetime
import os
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
    def save_history_to_file(self):
        # 📁 Création du dossier "exports" s'il n'existe pas
        export_dir = os.path.join(os.getcwd(), "exports")
        os.makedirs(export_dir, exist_ok=True)

        # 🕒 Nom par défaut avec timestamp
        default_filename = f"historique_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        default_path = os.path.join(export_dir, default_filename)

        # 💬 Fenêtre de dialogue
        path, _ = QFileDialog.getSaveFileName(
            self.view,
            "Enregistrer l'historique",
            default_path,
            "Fichiers JSON (*.json)"
        )

        if not path:
            return  # utilisateur a annulé

        if not path.endswith(".json"):
            path += ".json"

        try:
            # 🧼 Conversion des objets non-sérialisables
            serializable_history = []
            for msg in self.history:
                if isinstance(msg, HumanMessage):
                    serializable_history.append({"role": "user", "content": msg.content})
                elif isinstance(msg, AIMessage):
                    serializable_history.append({"role": "ai", "content": msg.content})

            with open(path, "w", encoding="utf-8") as f:
                json.dump(serializable_history, f, indent=2, ensure_ascii=False)

            print(f"✅ Historique enregistré avec succès dans : {path}")

        except Exception as e:
            self.view.display_error(f"Erreur lors de la sauvegarde : {str(e)}")

    def load_history_from_file(self, filepath):
        confirm = QMessageBox.StandardButton.Yes
        if self.history:
            confirm = QMessageBox.question(
                self.view,
                "Confirmation",
                "⚠️ Cette action va effacer la conversation actuelle. Voulez-vous continuer ?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
        if confirm == QMessageBox.StandardButton.No:
            return
        with open(filepath, "r", encoding="utf-8") as f:
            raw_history = json.load(f)

        self.history = []
        while self.view.chat_layout.count():
            child = self.view.chat_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        last_user_msg = None
        last_ai_msg = None

        for msg in raw_history:
            if msg["role"] == "user":
                if last_user_msg and last_ai_msg:
                    # Afficher la dernière réponse IA avant de passer au prochain user
                    self.view.display_response(last_ai_msg)

                self.history.append(HumanMessage(content=msg["content"]))
                self.view.append_message("Vous", msg["content"])
                last_user_msg = msg["content"]
                last_ai_msg = None

            elif msg["role"] == "ai":
                self.history.append(AIMessage(content=msg["content"]))
                last_ai_msg = msg["content"]

        # Affiche la dernière réponse IA si présente
        if last_ai_msg:
            self.view.display_response(last_ai_msg)
    def open_history_file_dialog(self):
        path, _ = QFileDialog.getOpenFileName(
            self.view,
            "Ouvrir un historique",
            "",
            "Fichiers JSON (*.json)"
        )
        if path:
            self.load_history_from_file(path)
    def _format_summary(self, state):
        print("📦 State keys: FORMAT_SUMMARY", list(state.keys()))
        req_init = state.get("request_call_initial", None)
        req = state.get("request_call", None)
        fonctions = state.get("traitement_format", None)
        traitements = state.get("traitements", None)

        print("🔍 Résumé des traitements :", state.get("traitements",None))

        """ if not req:
            req = state.get("request_call") """
        print("🔍 Résumé de la requête (call) :", req)
        print("🔍 Résumé de la requête (initial) :", req_init)
        if not req:
            return "🤷 Je n’ai pas pu extraire la requête utilisateur."

        lines = ["📋 <b>Résumé de la requête</b>"]

        
        lines.append(f"🧠 <b>Question</b> : {req_init.question_utilisateur}")
        lines.append(f"🎯 <b>Intention</b> : {req_init.intention}")
        lines.append(f"📂 <b>Type de traitement</b> : {req_init.type_traitement}")

        # 👉 Sinon, c’est un choix simple comme Choix(choix_dataFrames=[...])
        lines.append("✅ <b>DataFrames choisis pour affichage :</b>")
        for i, elem in enumerate(req.choix_dataFrames):
            lines.append(f"<div style='margin-left:20px'>📄 <b>   DataFrame {i+1}</b> : Index {elem.numero_dataFrame}</div>")
        if req_init.elements_cherches_request:
                el = req_init.elements_cherches_request[0]

                if el.periode_requete:
                    date_from = el.periode_requete.date_from.split("T")[0]
                    date_to = el.periode_requete.date_to.split("T")[0]
                    lines.append(f"🗓️ <b>Période</b> : {date_from} → {date_to}")

                if el.machine_request:
                    lines.append(f"🏭 <b>Machine</b> : {el.machine_request.name}")

                if el.variables_requete:
                    lines.append("🔧 <b>Variables de la requête</b> :")
                    for v in el.variables_requete:
                        lines.append(f"<div style='margin-left:20px'>➡️ <b>{v.role}</b> : {v.alias}</div>")

        if req_init.resultat_attendu:
            try:
                lines.append(f"📌 <b>Résultat attendu</b> : {', '.join(req_init.resultat_attendu)}")
            except TypeError:
                lines.append(f"📌 <b>Résultat attendu</b> : {req_init.resultat_attendu}")
        # Traitements effectués
        lines.append("🔧 <b>Traitements effectués</b> :")
        if traitements:
            for i, t in enumerate(traitements):
                lines.append(f"<div style='margin-left:20px'>➡️ Traitement {i + 1} : {t}</div>")
        else:
            lines.append("<div style='margin-left:20px'>➡️ Aucun traitement déclaré</div>")

        # Fonctions appelées
        # Fonctions appelées
        lines.append("<div style='margin-left:0px'>🛠️ <b>Fonctions appliquées :</b></div>")

        if fonctions and hasattr(fonctions, "fonction_appelee"):
            args_str = ', '.join(str(arg) for arg in fonctions.args)
            lines.append(f"<div style='margin-left:20px'>⚙️ <b>Fonction</b> : {fonctions.fonction_appelee.value} avec args {args_str}</div>")
        else:
            lines.append("<div style='margin-left:20px'>⚙️ Aucune fonction détectée ou applicable</div>")


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

