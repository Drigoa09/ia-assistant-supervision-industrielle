from pydantic import BaseModel, Field

from typing import Optional, List

from aenum import Enum

class periode(BaseModel):

    type : str = Field(description= "Type de la période")
    valeur : str = Field(description="Comment est réprésenté la période")

    date_from : str = Field(description = "Date de début de période au format ISO 8601")
    date_to : str = Field(description= "Date de fin de période au format ISO 8601")

DEBUT = 'Si la question_utilisateur contient : '

class Attribut_Principal(Enum):
    _init_ = 'value __doc__'

class Attribut(Enum):
    _init_ = 'value __doc__'
    NOM_PROGRAMME_SELECT = "property.nomProgrammeSelect", DEBUT + '"programme" ou "rendement de coupe"'
    NOM_OUTIL_BROCHE = "property.activeToolNumber", DEBUT + '"outil"'
    POWER_X = "property.power_X", DEBUT + '"outil"'
    POWER_Y = "property.power_Y", DEBUT + '"outil"'
    POWER_Z = "property.power_Z", DEBUT + '"outil"'
    POWER_SPINDLE = "property.powerSpindle", DEBUT + '"coût énergétique", ou "puissance"'
    POWER_A = "property.power_A", DEBUT + '"coût énergétique"**, ou **"puissance"'
    POWER_C = "property.power_C", DEBUT + '"coût énergétique", ou "puissance"'
    SPINdLOAD = "property.spindlLoad", DEBUT + '"charge de la broche" ou "couple"'
    ALARME = "property.numDerniereAlarme", DEBUT + '"alarme" ou "défaut"'
    CYCLE = "property.operatingTime", DEBUT + '"cycle".'
    TEMPS_DE_COUPE = "property.cuttingTime", DEBUT + '"coupe".'
    TEMPS_BROCHE_EXT = "property.tempBrocheExt", DEBUT + '"température" ou "chaleur"'
    SUM_CYCLE_TIME_NET = "property.sumCycleTimeNet", DEBUT + '"rendement de coupe"'

class Machine(Enum):
    Huron_KXFive = "logstash-huron-k3x8f-202*"
    SigScan = "sigscan"

class variable_principale(BaseModel):
    nom : Attribut_Principal = Field(description = "Nom de l'attribut de la variable principale parmi les énumérations")
    alias : str = Field(description = "Nom de la variable")
    role : str = Field(description = "Role de la variable")
    
class variable(BaseModel):
    nom : Attribut = Field(description = "Nom de l'attribut de la variable parmi les énumérations")
    alias : str = Field(description = "Nom de la variable")
    role : str = Field(description = "Role de la variable en une phrase complète.")

PERIODES = '''
🕓 **Période :**
- Si aucune période n’est mentionnée dans la question → considérer une période par défaut de 90 jours avant aujourd'hui
'''

MACHINES = '''
🗂️ **Sélection de la machine :**
- Par défaut → `logstash-huron-k3x8f-202*`
- Si la question mentionne **"sigscan"**, **"bac"**, ou **"géolocalisation"** → `sigscan`
'''

VARIABLES = '''
- Si la question_utilisateur contient "cycle" : `property.operatingTime`
- Si la question_utilisateur contient "coupe" : `property.cuttingTime`
- Si la question_utilisateur contient **"rendement de coupe"** → ajouter `property.sumCycleTimeNet`, `property.operatingTime`
- Si la question contient **"programme"** → ajouter `property.nomProgrammeSelect`
- Si elle contient **"outil"** → ajouter `property.activeToolNumber`
- Si elle contient **"mise sous tension"** ou **"allumée"** → ajouter `property.sumCycleTimeNet`
- Si elle contient **"consommation d’électricité"**, **"coût énergétique"**, ou **"puissance"** → ajouter `property.power_X`, `property.power_Y`, `property.power_Z`, `property.powerSpindle`, `property.power_A`, `property.power_C`
- Si elle contient **"charge de la broche"** ou **"couple"** → ajouter `property.spindlLoad`
- Si elle contient **"température"** ou **"chaleur"** → ajouter `property.tempBrocheExt`
- Si elle contient **"alarme"** ou **"défaut"** → ajouter `property.numDerniereAlarme`

'''

class elements_cherches(BaseModel):
    machine_request : Machine = Field(description="Machine où nous voulons obtenir les informations" + MACHINES)

    periode_requete : periode = Field(description="Période associée à la requête" + PERIODES)

    variables_requete : List[variable] = Field(description = "Associer les variables recherchées." + VARIABLES)

    description : str = Field(description = "Description des variables recherchées et explication de pourquoi ils sont là")

class request(BaseModel):
    """Format d'une requête à la base de donnée"""

    question_utilisateur : str = Field(description = "Question posée par l'utilisateur")
    intention : str = Field(description = "Intention de la requête")
    type_traitement : str = Field(description = "Type du traitement")

    elements_cherches_request : List[elements_cherches] = Field(description="Liste des éléments cherchés dans la base de données. On peut ajouter un autre élément à elements_cherches_request pour faire une autre requête. La description de elements_cherches explique leur rôle et ce qu'ils font")

    resultat_attendu : List[str] = Field("Liste des résultats attendus")