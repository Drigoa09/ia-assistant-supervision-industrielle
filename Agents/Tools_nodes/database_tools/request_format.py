from pydantic import BaseModel, Field

from typing import Optional, List

from aenum import Enum

class periode(BaseModel):

    type : str = Field(description= "Type de la période")
    valeur : str = Field(description="Comment est réprésenté la période")

    date_from : str = Field(description = "Date de début de période au format ISO 8601")
    date_to : str = Field(description= "Date de fin de période au format ISO 8601")

DEBUT = 'Si la question contient : '

class Attribut(Enum):
    _init_ = 'value __doc__'
    CYCLE = "property.operatingTime", DEBUT + '"cycle", "rendement de coupe", "consommation d’électricité", "coût énergétique", ou "puissance"'
    NOM_PROGRAMME_SELECT = "property.nomProgrammeSelect", DEBUT + '"programme" ou "rendement de coupe"'
    TEMPS_DE_COUPE = "property.cuttingTime", DEBUT + '"coupe"'
    NOM_OUTIL_BROCHE = "property.activeToolNumber", DEBUT + '"coupe" ou "outil"'
    SUM_CYCLE_TIME_NET = "property.sumCycleTimeNet", DEBUT + '"mise sous tension" ou "allumée"'
    POWER_X = "property.power_X", DEBUT + '"outil"'
    POWER_Y = "property.power_Y", DEBUT + '"outil"'
    POWER_Z = "property.power_Z", DEBUT + '"outil"'
    POWER_SPINDLE = "property.powerSpindle", DEBUT + '"coût énergétique", ou "puissance"'
    POWER_A = "property.power_A", DEBUT + '"coût énergétique"**, ou **"puissance"'
    POWER_C = "property.power_C", DEBUT + '"coût énergétique", ou "puissance"'
    SPINdLOAD = "property.spindlLoad", DEBUT + '"charge de la broche" ou "couple"'
    TEMPS_BROCHE_EXT = "property.tempBrocheExt", DEBUT + '"température" ou "chaleur"'
    ALARME = "property.numDerniereAlarme", DEBUT + '"alarme" ou "défaut"'

class Machine(Enum):
    Huron_KXFive = "logstash-huron-k3x8f-202*"
    SigScan = "sigscan"

class variable(BaseModel):
    nom : Attribut = Field(description = "Nom de l'attribut de la variable parmi les énumérations")
    alias : str = Field(description = "Nom de la variable")
    role : str = Field(description = "Role de la variable")

PERIODES = '''
🕓 **Période :**
- Si aucune période n’est mentionnée dans la question → considérer une période par défaut de 90 jours
'''

MACHINES = '''
🗂️ **Sélection de la machine :**
- Par défaut → `logstash-huron-k3x8f-202*`
- Si la question mentionne **"sigscan"**, **"bac"**, ou **"géolocalisation"** → `sigscan`
'''

VARIABLES = '''
- Si la question contient **"cycle"** ou **"programme"** → ajouter `property.operatingTime`, `property.nomProgrammeSelect`
- Si elle contient **"coupe"** ou **"outil"** → ajouter `property.cuttingTime`, `property.activeToolNumber`
- Si elle contient **"mise sous tension"** ou **"allumée"** → ajouter `property.sumCycleTimeNet`
- Si elle contient **"rendement de coupe"** → ajouter `property.operatingTime`, `property.cuttingTime`
- Si elle contient **"consommation d’électricité"**, **"coût énergétique"**, ou **"puissance"** → ajouter `property.operatingTime`, `property.power_X`, `property.power_Y`, `property.power_Z`, `property.powerSpindle`, `property.power_A`, `property.power_C`
- Si elle contient **"charge de la broche"** ou **"couple"** → ajouter `property.spindlLoad`
- Si elle contient **"température"** ou **"chaleur"** → ajouter `property.tempBrocheExt`
- Si elle contient **"alarme"** ou **"défaut"** → ajouter `property.numDerniereAlarme`

Variables de préférence en principale requete :
- property.operatingTime
- property.cuttingTime

'''

class request(BaseModel):
    """Format d'une requête à la base de donnée"""

    question_utilisateur : str = Field(description = "Question posée par l'utilisateur")
    machine_request : Machine = Field(description="Machine où nous voulons obtenir les informations" + MACHINES)
    intention : str = Field(description = "Intention de la requête")
    type_traitement : str = Field(description = "Type du traitement")

    programme_cible : Optional[str] = Field(description = "Programme cible associés à notre requête")

    periode_requete : periode = Field(description="Période associée à la requête" + PERIODES)

    variable_principale_requete : variable = Field(description = "Variable principale dont les variables contexte vont se baser. Représente l'abscisse dans un graphique. Mettre de préférence une variable temporelle ici." + VARIABLES)
    variables_contextes_requete : List[variable] = Field(description = "Variables contextes associées à la variable principale. Représente les ordonnées dans un graphique" + VARIABLES)

    resultat_attendu : List[str] = Field("Liste des résultats attendus")