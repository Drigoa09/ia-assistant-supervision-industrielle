from typing import Literal
from OrderState import OrderState
class Trieur_node():
    def sigscan_or_huron(self,state: OrderState) -> Literal["Créateur de tâches", "Formalisateur de requête"]:
        if state["Huron_related"]:
            return "Créateur de tâches"
        else:
            return "Formalisateur de requête"