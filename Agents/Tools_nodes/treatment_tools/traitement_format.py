from pydantic import BaseModel, Field

from typing import Optional, List

from aenum import Enum

class fonctions_existantes(Enum):
    _init_ = 'value __doc__'
    PLUS_OCCURENT = "plus_occurent", "Permet de connaître l'élément le plus occurent parmi les arguments proposés. Arguments : Liste des clés de dataFrame concernées"
    INFORMATION_EN_FONCTION_AUTRE = "information_en_fonction_autre", "Permet d'exprimer une information en fonction d'une autre information. Premier argument : élément de dataFrame dont dépendent les autres informations. Toujours mettre une variable temporelle en premier argument. Autres arguments : Les élément de dataFrame exprimées selon le premier argument"
    FILTRER_VALEUR = "filtrer_valeur", "Permet de filtrer des colonnes de DataFrame de sorte à ne les faire correspondre qu'à une valeur. Premier argument : Valeur correspondant à l'élément filtré.  2ème : Elément de dataFrame contenant l'élément filtré. 3ème arguments : Elément de dataFrame filtrée "
    FILTRER_COMPARAISON = "filtrer_comparaison", "Permet de filtrer des colonnes de DataFrame de sorte à ne garder que les valeurs comprises entre deux valeurs précises. Argument 1 : Colonne de dataFrame. Argument 2 : Valeur minimale. Si cette valeur est - infini, mettre -inf. Argument 3 : Valeur maximale. Si cette valeur est + infini, mettre +inf"
    CREER_GRAPHIQUE = "creer_graphique", "Permet de créer un graphique à partir de colonnes de dataframes. Argument 1 : Colonne de dataFrame correspondant à x. Argument 2 : colonne de dataFrame correspondant à y"

MESSAGE_FONCTION = '''
Pour plus_occurent : Permet de connaître l'élément le plus occurent parmi les arguments proposés.
---------------------------------------------------------------------------------------------------------------------------------------
Pour information_en_fonction_autre : Permet d'exprimer une information en fonction d'une autre information.
---------------------------------------------------------------------------------------------------------------------------------------
Pour filtrer_valeur : Permet de filtrer des colonnes de DataFrame de sorte à ne les faire correspondre qu'à une valeur.
---------------------------------------------------------------------------------------------------------------------------------------
Pour filtrer_comparaison : Permet de filtrer des colonnes de DataFrame de sorte à ne garder que les valeurs comprises entre deux valeurs précises.
---------------------------------------------------------------------------------------------------------------------------------------
Pour creer_graphique, permet de créer un graphique à partir de clés de dataframes.
'''

MESSAGE_ARGUMENTS = '''
Pour plus_occurent : Arguments : Liste des éléments de dataFrame concernées
---------------------------------------------------------------------------------------------------------------------------------------
Pour information_en_fonction_autre : 
    -Premier argument : élément de dataFrame dont dépendent les autres informations. Toujours mettre un élément contenant une variable temporelle en premier argument
    Les variables temporelles sont les temps cycles et les temps de coupe
    -Autres arguments : Les éléments de dataFrame exprimées selon le premier argument
    ---------------------------------------------------------------------------------------------------------------------------------------
Pour filtrer_valeur :
    -Premier argument : Valeur correspondant à l'élément filtré. 
    -2ème : Element de dataFrame contenant l'élément filtré
    -3ème arguments : Element de dataFrame filtrée 
    ---------------------------------------------------------------------------------------------------------------------------------------
Pour filtrer_comparaison :
    - Argument 1 : Colonne de dataFrame. 
    - Argument 2 : Valeur minimale. Si cette valeur est - infini, mettre -inf. 
    - Argument 3 : Valeur maximale. Si cette valeur est + infini, mettre +inf
    ---------------------------------------------------------------------------------------------------------------------------------------
Pour creer_graphique :
    Argument 1 : Colonne de dataFrame correspondant à x. 
    Argument 2 : colonne de dataFrame correspondant à y
'''
from typing import Union

class Element(BaseModel):

    numero_dataFrame : int = Field(description = "Numéro du dataFrame où est contenu l'élément")
    cle_dataFrame : str = Field(description= "Clé de DataFrame où se trouve l'élément")

class fonction(BaseModel):

    fonction_appelee : fonctions_existantes = Field(description = "Fonction appelée par l'agent" + MESSAGE_FONCTION)
    args : List[Union[Element, str]] = Field(description = "Liste des éléments à donner" + MESSAGE_ARGUMENTS)

class Traitement_Format(BaseModel):

    fonctions_appelees : List[fonction] = Field(description="Liste des fonctions appelées")
