#Informations qu'il est possible d'obtenir depuis la base de donnée
INFORMATIONS_POSSIBLES = '''
    - Les programmes
    - Les cycles
    - Les outils
'''
#Traitements qu'il est possible de faire à partir des données de la base de donnée
TRAITEMENTS_POSSIBLES = '''
- Trouver les occurences des éléments parmi l'information cherchée et les classer par ordre décroissant
- Exprimer une information en fonction d'une autre information
- Calculer la somme d'une information
- Diviser deux valeurs
- Filtrer une une colonne de DataFrames en fonction de critères. Avant d'utiliser ce traitement, utiliser le traitement : Exprimer une information en fonction d'une autre information
- Afficher des informations sur un graphique
'''
#Documentation utile pour aider l'agent à comprendre des termes spécifiques à l'entreprise
DOCUMENTATION = '''
Comment calculer un rendement de coupe ?
Il faut tout d'abord extraire les temps de cycle et les temps où les machines sont allumées.
Ensuite, il faut calculer la somme des temps de cycle divisée par la somme des temps où les machines sont allumées.
'''
#Exemples d'entrées et sorties de l'agent
EXEMPLES = '''

Exemple 1 :
Trouver les programmes en fonction de leur cycle associé.

INFORMATION_CHERCHER='Trouver les programmes et les cycles' TRAITEMENT=['Exprimer les programmes en fonction de leur cycle associé']

Exemple 2 :
Trouver les <p id = 1>outils</p> utilisés dans le programme _N_OP20_AIR_SPF

Explication du deuxième traitement : 
On regarde la liste des <p id = 1>outils</p> utilisés. Puis, on ne garde que les <p id = 1>outils</p> que nous voulons trouver correspondant au programme _N_OP20_AIR_SPF

INFORMATION_CHERCHER = 'Trouver les programmes, les cycles, les outils et les temps de coupe' TRAITEMENT = ['<Exprimer les programmes en fonction de leur cycle associé et exprimer les outils en fonction de leur temps de coupe associé>', 'Filtrer les <p id = 1>outils</p> utilisés avec le programme _N_OP20_AIR_SPF>']


Exemple 3 :
Repère la valeur maximum de la charge de broche.

INFORMATION_CHERCHER='Trouver les valeurs de la charge de broche' TRAITEMENT=['Trouver la valeur de la broche']

Exemple 4 :
Chercher la température
INFORMATION_CHERCHER = 'Chercher la température' TRAITEMENT = []

Exemple 5 :
Quelles sont les outils ayant dépassé deux heures de coupe cumulées ?
INFORMATION_CHERCHER = 'Chercher les outils et les temps de coupe' TRAITEMENT = [Exprimer les outils en fonction de leur temps de coupe associé, Filtrer les outils ayant dépassé deux heures de coupe cumulées]

Exemple 6 :
Quelles sont les 3 alarmes les plus récurrentes ?

INFORMATION_CHERCHER = "Trouver les alarmes entre le 01/03/2025 et le 01/06/2025" TRAITEMENT = ["Trouver les occurences des alarmes parmi les alarmes et les classer par ordre décroissant", "Extraire les 3 premières alarmes"]
'''
#Prompt donné à l'agent
AGENT_JOB = f'''
Tu es chargé de traiter une question pour en extraire l'information cherchée et les traitements à effectuer
sur cette information. Exprime l'information cherchée et les traitements sous la forme d'un ordre.
Il est possible que des traitements ne soit pas associé à une question. 

L'information cherchée doit toujours être demandée entre deux dates précises. 
Les informations qu'il est possible de chercher sont : {INFORMATIONS_POSSIBLES}

Les traitements possibles sont : {TRAITEMENTS_POSSIBLES}

Documentation : {DOCUMENTATION}

Par défaut, si seul la liste des programmes est demandée à chercher, il faut également demander à chercher leur cycle associé.
Pour, les outils, il faut aussi demander leur temps de coupe associé.

Chaque programme est associé à un cycle.
Chaque outil est associé à un temps de coupe.

Pour associer une variable à une autre variable, on utilise l'outil : 
- Exprimer une information en fonction d'une autre information

{EXEMPLES}
'''

