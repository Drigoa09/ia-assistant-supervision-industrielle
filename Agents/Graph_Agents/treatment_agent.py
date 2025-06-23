from OrderState import OrderState
from model import model_codestral

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

[fonction(fonction_appelee=<fonctions_existantes.FILTRER: 'filtrer'>, args=['130', Element(numero_dataFrame=numéro correspondant aux outils, cle_dataFrame=clé correspondant aux outils), Element(numero_dataFrame=numéro correspondant aux programmes, cle_dataFrame=clé correspondant aux programmes)])]
'''

def treatment_agent(state: OrderState) -> OrderState:
    """The chatbot itself. A wrapper around the model's own chat interface."""

    if state['traitement'] != None:
        AGENT_GENERATION_SYSINT = '''
        Tu es un agent interprète spécialisé dans l’industrie.

        Tu essaies de répondre aux questions avec les outils qui te sont donnés, pas à pas.
        Tu as accès aux clés de dataFrame : \n

        timestamp signifie le temps où la donnée a été prise
        '''
        n = len(state['dataFrames'])
        
        for i in range(n):
            AGENT_GENERATION_SYSINT +=  f"Emplacement : {i} et colonnes : {state['dataFrames'][i].dataFrame.columns}" + " : " + state['dataFrames'][i].role + "\n"

        AGENT_GENERATION_SYSINT += '''Tu ne peux utiliser que ces clés de dataFrame. Il n'est pas possible d'en utiliser des variantes'''

        AGENT_GENERATION_SYSINT += EXEMPLES

        print("Prompt donné : \n")
        print(AGENT_GENERATION_SYSINT)

        state['request_call'] = structured_llm.invoke([AGENT_GENERATION_SYSINT, state['traitement']])

        print(state['request_call'])

    return state