from langchain_core.messages.ai import AIMessage

from Tools_nodes.treatment_tools.traitement_format import fonctions_existantes

import OrderState

def plus_occurent(dataFrames, args, args_restants):

    new_dataFrames = []

    for arg in args:
        for dataFrame in dataFrames:
            if arg in dataFrame.columns:
                new_dataFrames.append(dataFrame[arg].value_counts().to_frame())
                break

    for arg in args:
        args_restants.append(arg)

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

    for dataFrame in dataFrames:
        if arg0 in dataFrame.columns:
            df_tempsCycle = dataFrame

    for arg in args[1:]:
        args_restants.append(arg)

    if df_tempsCycle is None or df_tempsCycle.empty:
        return "Aucun cycle détecté."
    
    dfs_programmes = []

    for field_contexte in args[1:]:
        for dataFrame in dataFrames:
            if field_contexte in dataFrame.columns:
                dfs_programmes.append(dataFrame)

    # Découpage des cycles en intervalles
    periodes = extraire_intervalles(df_tempsCycle, dfs_programmes, args[1:])

    # Affichage final
    df_final = pd.DataFrame.from_dict(periodes, orient="index")
    df_final["start"] = pd.to_datetime(df_final["start"]).dt.strftime('%Y-%m-%d %H:%M:%S')
    df_final["end"] = pd.to_datetime(df_final["end"]).dt.strftime('%Y-%m-%d %H:%M:%S')

    new_dataFrames.append(df_final)

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

        state['dataFrames'] = new_dataFrames
        state['dataFrames_columns'] = args_restants

        message = ""

        for (dataFrame_index) in new_dataFrames:
            message += dataFrame_index.to_html()

        new_output = {"messages" : [AIMessage(content=message)]}

        return state | new_output
    
    else:
        
        return state