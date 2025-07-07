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

from index import formalisateur_requete

class ChatController:
    style = "padding-left: 20px; margin: 0; white-space: pre-wrap; font-family: Consolas, monospace; line-height: 1.4em;"

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
    def display_welcome_message(self):
        welcome = (
            "👋 Bonjour ! Je suis votre assistant pour la supervision industrielle.\n"
            "Posez-moi une question sur les machines, les outils, les alarmes ou la production !"
        )
        self.view.display_response(welcome)
        self.history.append(AIMessage(content=welcome))  # 🔄 Historique

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
        req = state.get("request_call", None)

        if state.get("Huron_related"):
            req_init = state.get("request_call_initial", None)
        else:
            req_init = req
        fonctions = state.get("traitement_format", None)
        traitements = state.get("traitements", None)
        input_tokens = state.get("latest_input_tokens", None)
        output_tokens = state.get("latest_output_tokens", None)

        if not req:
            return "🤷 Je n’ai pas pu extraire la requête utilisateur."

        if type(req_init) != formalisateur_requete.dict_Structure:
            lines = []
            lines.append("📋 Résumé de la requête\n")
            lines.append("Nombre de tokens utilisés:\n")
            lines.append(f"    ➡️ Tokens d'entrée : {input_tokens}")
            lines.append(f"    ➡️ Tokens de sortie : {output_tokens}\n")
            lines.append(f"🧠 Question : {req_init.question_utilisateur}")
            lines.append(f"🎯 Intention : {req_init.intention}")
            lines.append(f"📂 Type de traitement : {req_init.type_traitement}\n")
            if hasattr(req, "choix_dataFrames"):
                lines.append("✅ DataFrames choisis pour affichage :")
                for i, elem in enumerate(req.choix_dataFrames):
                    lines.append(f"    📄 DataFrame {i + 1} : Index {elem.numero_dataFrame}")

            if req_init.elements_cherches_request:
                el = req_init.elements_cherches_request[0]

                if el.periode_requete:
                    date_from = el.periode_requete.date_from.split("T")[0]
                    date_to = el.periode_requete.date_to.split("T")[0]
                    lines.append(f"\n🗓️ Période : {date_from} → {date_to}")
                if el.machine_request:
                    lines.append(f"🏭 Machine : {el.machine_request.name}")
                if el.variables_requete:
                    lines.append("🔧 Variables de la requête :")
                    for v in el.variables_requete:
                        lines.append(f"    ➡️ {v.role} : {v.alias}")

            if req_init.resultat_attendu:
                try:
                    lines.append(f"\n📌 Résultat attendu : {', '.join(req_init.resultat_attendu)}")
                except TypeError:
                    lines.append(f"📌 Résultat attendu : {req_init.resultat_attendu}")

            lines.append("\n🔧 Traitements effectués :")
            if traitements:
                for i, t in enumerate(traitements):
                    lines.append(f"    ➡️ Traitement {i + 1} : {t}")
            else:
                lines.append("    ➡️ Aucun traitement déclaré")

            lines.append("\n🛠️ Fonctions appliquées :")
            if fonctions and hasattr(fonctions, "fonction_appelee"):
                args_str = ', '.join(str(arg) for arg in fonctions.args)
                lines.append(f"    ⚙️ Fonction : {fonctions.fonction_appelee.value} avec args {args_str}")
            else:
                lines.append("    ⚙️ Aucune fonction détectée ou applicable")
        else:
            lines = []
            if req_init.object:
                lines.append(f"Objet(s) recherché(s): {req_init.object}")
            else:
                lines.append("Objet(s) recherché(s): Tous les objets")
            if req_init.area:
                lines.append(f"Zone(s) recherchée(s): {req_init.area}")
            else:
                lines.append("Zone(s) recherchée(s): Toutes les zones")
            if req_init.startDate and req_init.endDate:
                lines.append(f"Période: {req_init.startDate} ->  {req_init.endDate}")
            else:
                lines.append("Période: 90 jours avant aujourd'hui")

        # 💡 Converti le tout dans un bloc HTML <pre> avec style propre
        content = "\n".join(lines)
        return f"<pre style='font-family: Consolas, monospace; font-size: 13px; line-height: 1.4em; white-space: pre-wrap; margin: 0;'>{content}</pre>"


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
            Q_ARG(str, str(error_msg))
        )

