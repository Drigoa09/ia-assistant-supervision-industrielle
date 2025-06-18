from pydantic import BaseModel, Field

from typing import Optional, List

from aenum import Enum

class fonctions_existantes(Enum):
    _init_ = 'value __doc__'
    PLUS_OCCURENT = "plus_occurent", "Permet de connaître l'élément le plus occurent parmi les arguments proposés. Arguments : Liste des clés de dataFrame concernées"

class fonction(BaseModel):

    fonction_appelee : fonctions_existantes = Field(description = "Fonction appelée par l'agent")
    args : List[str] = Field(description = "Liste des arguments à donner")

class Traitement_Format(BaseModel):

    fonctions_appelees : List[fonction] = Field(description="Liste des fonctions appelées")
