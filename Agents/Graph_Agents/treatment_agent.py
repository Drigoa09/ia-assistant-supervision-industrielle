from OrderState import OrderState
from model import model_codestral, model_mistral_medium

from Tools_nodes.treatment_tools.traitement_format import Traitement_Format

structured_llm = model_codestral.with_structured_output(Traitement_Format)

EXEMPLES = '''
Exemple 1 :
Exprimer les programmes en fonction de leur cycle associé

[fonction(fonction_appelee=<fonctions_existantes.INFORMATION_EN_FONCTION_AUTRE: 'information_en_fonction_autre'>, args=[DataFrame contenant les cycles, DataFrame contenant les programmes)]

Exemple 2 :
Afficher les informations sur un graphique

[fonction(fonction_appelee=<fonctions_existantes.CREER_GRAPHIQUE: 'creer_graphique'>, args=[DataFrames contenant les graphiques que nous voulons afficher]]

Exemple 3 :
Filtrer les programmes en acceptant que ceux contenant l'outil 130

[fonction(fonction_appelee=<fonctions_existantes.FILTRER_VALEUR: 'filtrer_valeur'>, args=['130', Element(numero_dataFrame=numéro correspondant aux outils, cle_dataFrame=clé correspondant aux outils), Element(numero_dataFrame=numéro correspondant aux programmes, cle_dataFrame=clé correspondant aux programmes)])]

Exemple 4 :
Filtrer les outils ayant dépassé deux heures de coupe cumulées

N'oublie pas que les numéros de dataFrame et leur clé doit exister

[fonction(fonction_appelee=<fonctions_existantes.FILTRER_COMPARAISON: 'filtrer_comparaison'>, args=[Element(numero_dataFrame=numéro correspondant au temps, cle_dataFrame=clé correspondant au temps), '7200', '+inf']

Exemple 5:
Extraire les 3 premières alarmes

[fonction(fonction_appelee=<fonctions_existantes.N_PREMIERS: 'filtrer_comparaison'>, args=[Element(numero_dataFrame=numéro correspondant aux alarmes, cle_dataFrame=clé correspondant aux alarmes), '3']
'''

def treatment_agent(state: OrderState) -> OrderState:
    """Agent de traitement"""

    if state['traitement'] != None:
        AGENT_GENERATION_SYSINT = '''
        Tu es un agent interprète spécialisé dans l’industrie.

        Tu essaies de répondre aux questions avec les outils qui te sont donnés, pas à pas.
        Tu as accès aux clés de dataFrame : \n

        timestamp signifie le temps où la donnée a été prise
        timestamp n'existe pas forcément.
        D'autres variables peuvent représenter le temps

        '''
        n = len(state['dataFrames'])
        
        for i in range(n):
            AGENT_GENERATION_SYSINT +=  f"Emplacement : {i} et colonnes : {state['dataFrames'][i].dataFrame.columns}" + " : " + state['dataFrames'][i].role + "\n"

        AGENT_GENERATION_SYSINT += '''Tu ne peux utiliser que ces clés de dataFrame. Il n'est pas possible d'en utiliser des variantes'''

        AGENT_GENERATION_SYSINT += EXEMPLES

        print("Prompt donné : \n")
        print(AGENT_GENERATION_SYSINT)

    traitement_actuel = state.get("traitement", "")
    prompt = f"{AGENT_GENERATION_SYSINT}\n{traitement_actuel}"

    # Appelle le modèle avec prompt fusionné
    traitement_format_result = structured_llm.invoke(prompt)

    #print("🧪 Résultat traitement_format:", traitement_format_result)

    # Tu crées un NOUVEAU dict propre ici
    updated_state = {
        **state,
        "traitement_format": traitement_format_result
    }

    #print("📤 Ce que je retourne dans treatment_agent:", list(updated_state.keys()))

    return updated_state