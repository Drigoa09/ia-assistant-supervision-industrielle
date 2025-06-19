from pydantic import BaseModel, Field

from typing import Optional, List

from aenum import Enum

class fonctions_existantes(Enum):
    _init_ = 'value __doc__'
    PLUS_OCCURENT = "plus_occurent", "Permet de connaître l'élément le plus occurent parmi les arguments proposés. Arguments : Liste des clés de dataFrame concernées"
    INFORMATION_EN_FONCTION_AUTRE = "information_en_fonction_autre", "Permet d'exprimer une information en fonction d'une autre information. Premier argument : clé de dataFrame dont dépendent les autres informations. Toujours mettre cycle, operatingTime, temps_coupe ou cuttingTime en premier argument. Autres arguments : Les clés de dataFrame exprimées selon le premier argument"
    FILTRER = "filtrer", "Permet de filtrer des colonnes de DataFrame de sorte à ne les faire correspondre qu'à une valeur. Premier argument : Valeur correspondant à l'élément filtré.  2ème : Clé de dataFrame filtré contenant l'élément filtré. 3ème arguments : Clé de dataFrame filtrée "

MESSAGE_FONCTION = '''
Pour plus_occurent : Permet de connaître l'élément le plus occurent parmi les arguments proposés.
Pour information_en_fonction_autre : Permet d'exprimer une information en fonction d'une autre information.
Pour filtrer : Permet de filtrer des colonnes de DataFrame de sorte à ne les faire correspondre qu'à une valeur. Toujours utilisé sur des colonnes de DataFrame traitées par information_en_fonction_autre_avant
'''

MESSAGE_ARGUMENTS = '''
Pour plus_occurent : Arguments : Liste des clés de dataFrame concernées
Pour information_en_fonction_autre : 
    -Premier argument : clé de dataFrame dont dépendent les autres informations. Toujours mettre une variable temporelle en premier argument
    -Autres arguments : Les clés de dataFrame exprimées selon le premier argument
Pour filtrer :
    -Premier argument : Valeur correspondant à l'élément filtré. 
    -2ème : Clé de dataFrame filtré contenant l'élément filtré
    -3ème arguments : Clé de dataFrame filtrée 
'''

class fonction(BaseModel):

    fonction_appelee : fonctions_existantes = Field(description = "Fonction appelée par l'agent" + MESSAGE_FONCTION)
    args : List[str] = Field(description = "Liste des arguments à donner" + MESSAGE_ARGUMENTS)

class Traitement_Format(BaseModel):

    fonctions_appelees : List[fonction] = Field(description="Liste des fonctions appelées")
