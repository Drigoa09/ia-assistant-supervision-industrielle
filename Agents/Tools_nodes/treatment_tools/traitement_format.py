from pydantic import BaseModel, Field

from typing import Optional, List

from aenum import Enum

class fonctions_existantes(Enum):
    _init_ = 'value __doc__'
    PLUS_OCCURENT = "plus_occurent", "Permet de connaître l'élément le plus occurent parmi les arguments proposés. Arguments : Liste des clés de dataFrame concernées"
    INFORMATION_EN_FONCTION_AUTRE = "information_en_fonction_autre", "Permet d'exprimer une information en fonction d'une autre information. Premier argument : clé de dataFrame dont dépendent les autres informations. Toujours mettre cycle, operatingTime, temps_coupe ou cuttingTime en premier argument. Autres arguments : Les clés de dataFrame exprimées selon le premier argument"

MESSAGE = '''
Pour plus_occurent : Arguments : Liste des clés de dataFrame concernées
Pour information_en_fonction_autre : 
    -Premier argument : clé de dataFrame dont dépendent les autres informations. Toujours mettre une variable temporelle en premier argument
    -Autres arguments : Les clés de dataFrame exprimées selon le premier argument
'''

class fonction(BaseModel):

    fonction_appelee : fonctions_existantes = Field(description = "Fonction appelée par l'agent" + MESSAGE)
    args : List[str] = Field(description = "Liste des arguments à donner" + MESSAGE)

class Traitement_Format(BaseModel):

    fonctions_appelees : List[fonction] = Field(description="Liste des fonctions appelées")
