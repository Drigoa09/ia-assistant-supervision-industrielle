from Tools_nodes.database_node.database_node import DataFrameRole

# Extraire les intervalles de cycle
def extraire_intervalles(df_source, df_contextes, variables_contextes, moment, seuil_pause=5):
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

            if moment == "avant":
                matching = df_contexte[df_contexte["timestamp"] < start]
                programme = str(matching.iloc[-1][nom_variable]) if not matching.empty else None
            else: #moment == "pendant" Comportement par défaut
                programme = df_contexte[df_contexte["timestamp"] > start]
                programme = programme[programme["timestamp"] < end]

            periodes[f"interval_{i}"][nom_variable] = programme

    return periodes

import pandas as pd
    
def exprimer_information_en_fonction_autre(dataFrames, args):

    new_dataFrames = dataFrames

    arg0 = args[0]
    arg1 = args[1]

    df_tempsCycle = dataFrames[arg1.numero_dataFrame].dataFrame

    if df_tempsCycle is None or df_tempsCycle.empty:
        return "Aucun cycle détecté."
    
    dfs_programmes = []

    names = []

    role = ""
    for field_contexte in args[2:]:
        dfs_programmes.append(dataFrames[field_contexte.numero_dataFrame].dataFrame)
        names.append(field_contexte.cle_dataFrame)
        role += dataFrames[field_contexte.numero_dataFrame].role + " associé à " + dataFrames[arg1.numero_dataFrame].role

    # Découpage des cycles en intervalles
    periodes = extraire_intervalles(df_tempsCycle, dfs_programmes, names, arg0)

    # Affichage final
    df_final = pd.DataFrame.from_dict(periodes, orient="index")
    df_final["start"] = pd.to_datetime(df_final["start"]).dt.strftime('%Y-%m-%d %H:%M:%S')
    df_final["end"] = pd.to_datetime(df_final["end"]).dt.strftime('%Y-%m-%d %H:%M:%S')

    new_dataFrames.append(DataFrameRole(df_final, role))

    return new_dataFrames
