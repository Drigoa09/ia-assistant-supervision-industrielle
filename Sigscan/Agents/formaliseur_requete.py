from enum import Enum
from State import State

from pydantic import create_model, Field
from Requetes.Agent_to_InteractionBdd import fields

from typing import Optional

import model

class Formalisateur_requete:

    def __init__(self, prompt_debut : str, objets : Enum, areas : Enum):
        self.prompt_debut = prompt_debut

        fields['object'] = (Optional[objets], Field(default=None, description = "Nom de l'objet dont nous voulons connaître les positions. Définir à None si aucun nom d'objet n'est mentionné"))
        fields['area'] = (Optional[areas], Field(default = None, description = "Nom de la zone dont nous voulons connaître les informations. Définir à None si aucune nom de zone n'est mentionnée"))

        self.fields = fields
        self.dict_Structure = create_model("dict_Structure", **fields)

        self.model = model.model_codestral.with_structured_output(self.dict_Structure)

    def formaliser_requete(self, state : State) -> State:

        request = self.model.invoke([self.prompt_debut, state['question']])

        state['call_request'] = request

        return state
