from langchain_core.messages.ai import AIMessage

from Tools_nodes.treatment_tools.traitement_format import fonctions_existantes

import OrderState

import matplotlib.pyplot as plt

from Tools_nodes.database_node import DataFrameRole

def creer_graphique(dataFrames, args, args_restants):
    plt.plot(dataFrames[args[0].numero_dataFrame].dataFrame[args[0].cle_dataFrame], dataFrames[args[1].numero_dataFrame].dataFrame[args[1].cle_dataFrame])
    plt.show()

    return []

"""
Les outils utilisés sont inclus dans des temps de coupe.
Les temps de coupe sont inclus dans des programmes
Les programmes sont inclus dans des temps de cycles.
"""

def filtrer(dataFrames, args, args_restants):

    new_dataFrames = []

    programme_cible = args[0]
    arg1 = args[1]
    arg2 = args[2]
    
    cycles_fonctionnement = dataFrames[args[1].numero_dataFrame].dataFrame
    cycles_coupe = dataFrames[args[2].numero_dataFrame].dataFrame

    cycles_programme_cible = [(v["start"], v["end"]) for v in cycles_fonctionnement.to_dict(orient = "index").values() 
                              if str(v[args[1].cle_dataFrame]) == programme_cible
                              ]

    #  Filtrer les cycles de coupe inclus dans les cycles du programme cible
    outils_utilisés = set()
    for v in cycles_coupe.to_dict(orient = "index").values():
        start_coupe = v["start"]
        outil = v[args[2].cle_dataFrame]
        for start_prog, end_prog in cycles_programme_cible:
            if (start_prog <= start_coupe <= end_prog) and outil is not None:
                outils_utilisés.add(outil)
                break

    dataFrame = pd.DataFrame(list(outils_utilisés))
    print(args[2])
    dataFrame.columns = [args[2].cle_dataFrame]
    new_dataFrames.append(DataFrameRole(dataFrame, []))

    return new_dataFrames

def plus_occurent(dataFrames, args, args_restants):

    new_dataFrames = []

    for arg in args:
        frame = dataFrames[arg.numero_dataFrame].dataFrame[arg.cle_dataFrame].value_counts().to_frame()
        frame.columns = [arg.cle_dataFrame]
        new_dataFrames.append(DataFrameRole(frame, dataFrames[arg.numero_dataFrame].role))

    for arg in args:
        args_restants.append(arg.cle_dataFrame)

    return new_dataFrames

# Extraire les intervalles de cycle
def extraire_intervalles(df_source, df_contextes, variables_contextes, seuil_pause=5):
    df_source = df_source.copy()
    df_source["time_diff"] = df_source["timestamp"].diff().dt.total_seconds()
    split_indices = df_source.index[df_source["time_diff"] > seuil_pause].tolist()
    sub_tables = [df_source.iloc[start:end] for start, end in zip([0]+split_indices, split_indices+[len(df_source)]) if end - start > 1]
    df_source.drop(columns="time_diff", inplace=True)

    periodes = {}
    for i, table in enumerate(sub_tables, 1):
        start, end = table["timestamp"].iloc[0], table["timestamp"].iloc[-1]
        duration = (end - start).total_seconds()
        
        periodes[f"interval_{i}"] = {
            "start": start,
            "end": end,
            "temps(s)": round(duration, 1)
        }

        for j in range(len(df_contextes)):

            df_contexte = df_contextes[j]
            nom_variable = variables_contextes[j]

            matching = df_contexte[df_contexte["timestamp"] < start]
            
            programme = str(matching.iloc[-1][nom_variable]) if not matching.empty else None
            periodes[f"interval_{i}"][nom_variable] = programme

    return periodes

import pandas as pd
    
def exprimer_information_en_fonction_autre(dataFrames, args, args_restants):

    new_dataFrames = []

    arg0 = args[0]

    df_tempsCycle = dataFrames[arg0.numero_dataFrame].dataFrame

    if df_tempsCycle is None or df_tempsCycle.empty:
        return "Aucun cycle détecté."
    
    dfs_programmes = []

    names = []

    role = ""
    for field_contexte in args[1:]:
        dfs_programmes.append(dataFrames[field_contexte.numero_dataFrame].dataFrame)
        names.append(field_contexte.cle_dataFrame)
        role += dataFrames[field_contexte.numero_dataFrame].role

    # Découpage des cycles en intervalles
    periodes = extraire_intervalles(df_tempsCycle, dfs_programmes, names)

    # Affichage final
    df_final = pd.DataFrame.from_dict(periodes, orient="index")
    df_final["start"] = pd.to_datetime(df_final["start"]).dt.strftime('%Y-%m-%d %H:%M:%S')
    df_final["end"] = pd.to_datetime(df_final["end"]).dt.strftime('%Y-%m-%d %H:%M:%S')

    new_dataFrames.append(DataFrameRole(df_final, role))

    return new_dataFrames


def treatment_node(state: OrderState) -> OrderState:
    """The chatbot itself. A wrapper around the model's own chat interface."""

    if state['traitement'] != None:

        fonctions_appelees = state['request_call'].fonctions_appelees


        args_restants = []
        new_dataFrames = []

        for fonction_appelee in fonctions_appelees:
            
            if fonction_appelee.fonction_appelee == fonctions_existantes.PLUS_OCCURENT:
                
                new_dataFrames += plus_occurent(state['dataFrames'], fonction_appelee.args, args_restants)

            elif fonction_appelee.fonction_appelee == fonctions_existantes.INFORMATION_EN_FONCTION_AUTRE:

                new_dataFrames += exprimer_information_en_fonction_autre(state['dataFrames'], fonction_appelee.args, args_restants)

            elif fonction_appelee.fonction_appelee == fonctions_existantes.FILTRER:

                new_dataFrames += filtrer(state['dataFrames'], fonction_appelee.args, args_restants)

            elif fonction_appelee.fonction_appelee == fonctions_existantes.CREER_GRAPHIQUE:

                new_dataFrames += creer_graphique(state['dataFrames'], fonction_appelee.args, args_restants)


        state['dataFrames'] = new_dataFrames
        state['dataFrames_columns'] = args_restants

        message = ""

        for (dataFrame_index) in new_dataFrames:
            message += dataFrame_index.dataFrame.to_html()

        new_output = {"messages" : [AIMessage(content=message)]}

        return state | new_output
    
    else:
        
        return state