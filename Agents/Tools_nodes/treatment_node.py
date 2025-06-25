from langchain_core.messages.ai import AIMessage

from Tools_nodes.treatment_tools.traitement_format import fonctions_existantes

import OrderState

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from Tools_nodes.database_node import DataFrameRole

def creer_graphique(dataFrames, args, args_restants):
    fig = Figure()
    ax = fig.add_subplot(111)
    x = dataFrames[args[0].numero_dataFrame].dataFrame[args[0].cle_dataFrame]
    y = dataFrames[args[1].numero_dataFrame].dataFrame[args[1].cle_dataFrame]
    ax.plot(x,y)
    ax.set_xlabel(args[0].cle_dataFrame)
    ax.set_ylabel(args[1].cle_dataFrame)
    ax.set_title("Graphique de " + args[1].cle_dataFrame + " en fonction de " + args[0].cle_dataFrame)

    return fig

def choisir_dataFrame(dataFrames, args):

    new_dataFrames = []

    for arg in args:
        new_dataFrames.append(dataFrames[arg.numero_dataFrame])

    print(new_dataFrames)

    return new_dataFrames

"""
Les outils utilisés sont inclus dans des temps de coupe.
Les temps de coupe sont inclus dans des programmes
Les programmes sont inclus dans des temps de cycles.
"""

def filtrer_valeur(dataFrames, args):

    new_dataFrames = dataFrames

    programme_cible = args[0]
    
    cycles_fonctionnement = dataFrames[args[1].numero_dataFrame].dataFrame
    cycles_coupe = dataFrames[args[2].numero_dataFrame].dataFrame

    cycles_programme_cible = [(v["start"], v["end"]) for v in cycles_fonctionnement.to_dict(orient = "index").values() 
                              if str(v[args[1].cle_dataFrame]) == programme_cible
                              ]

    #  Filtrer les cycles de coupe inclus dans les cycles du programme cible
    outils_utilisés = set()
    for v in cycles_coupe.to_dict(orient = "index").values():

        if "start" in v:
            start_coupe = v["start"]
        else:
            start_coupe = str(v["timestamp"])

        outil = v[args[2].cle_dataFrame]
        for start_prog, end_prog in cycles_programme_cible:
            if (start_prog <= start_coupe <= end_prog) or ("start" in v and start_coupe <= start_prog <= v["end"]) and outil is not None:
                outils_utilisés.add(outil)
                break

    dataFrame = pd.DataFrame(list(outils_utilisés), columns=[args[2].cle_dataFrame])
    
    new_dataFrames.append(DataFrameRole(dataFrame, dataFrames[args[2].numero_dataFrame].role + " Filtré par la fonction filtrer_valeur"))

    return new_dataFrames

def n_premiers(dataFrames, args):

    new_dataFrames = dataFrames

    dataFrame = dataFrames[args[0].numero_dataFrame].dataFrame

    new_dataFrames.append(DataFrameRole(dataFrame.head(int(args[1])), dataFrames[args[0].numero_dataFrame].role + " Filtré par n_premiers."))

    return new_dataFrames


from datetime import datetime

def is_valid_date(s: str, fmt: str) -> bool:
    try:
        datetime.strptime(s, fmt)
        return True
    except ValueError:
        return False

def filtrer_comparaison(dataFrames, args):
    
    new_dataFrames = dataFrames

    dataFrames_columns = dataFrames[args[0].numero_dataFrame].dataFrame[args[0].cle_dataFrame]

    if args[1] == "-inf":
        inf = -float('inf')
    else:
        inf = args[1]

    if args[2] == "+inf":
        sup = float('inf')
    else:
        sup = args[2]

    if is_valid_date(inf, "%H:%M:%S") or is_valid_date(sup, "%H:%M:%S"):
        df = dataFrames[args[0].numero_dataFrame].dataFrame
        
        if inf != -float('inf'):
            df = df[pd.to_datetime(dataFrames_columns, utc=True).dt.time > pd.to_datetime(inf).time()]
        if sup != float('inf'):
            df = df[pd.to_datetime(dataFrames_columns, utc=True).dt.time < pd.to_datetime(sup).time()]
    else:
        df = dataFrames[args[0].numero_dataFrame].dataFrame[inf < dataFrames_columns]
        df = df[dataFrames_columns < sup]

    new_dataFrames.append(DataFrameRole(df, dataFrames[args[0].numero_dataFrame].role + " Filtré par la fonction filtrer_comparaison"))

    return new_dataFrames

def plus_occurent(dataFrames, args):

    new_dataFrames = dataFrames

    for arg in args:
        frame = dataFrames[arg.numero_dataFrame].dataFrame[arg.cle_dataFrame].value_counts().to_frame()
        frame.columns = ["Occurences"]
        new_dataFrames.append(DataFrameRole(frame, dataFrames[arg.numero_dataFrame].role))

    return new_dataFrames

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


def treatment_node(state: OrderState) -> OrderState:
    """The chatbot itself. A wrapper around the model's own chat interface."""
    print("📦 State reçu dans treatment_node:", list(state.keys()))
    print("🔍 traitement_format vaut:", state.get("traitement_format"))

    if state['traitement'] != None:

        # 🔁 Tentative de récupération sécurisée
        traitement_format = state.get("traitement_format")
        if traitement_format is None:
            raise ValueError("❌ traitement_format est totalement absent, même en fallback ! Clés disponibles : " + str(state.keys()))

        args_restants = []
        new_dataFrames = []

        fonction_appelee = traitement_format
            
        if fonction_appelee.fonction_appelee == fonctions_existantes.PLUS_OCCURENT:
            
            new_dataFrames += plus_occurent(state['dataFrames'], fonction_appelee.args)

        elif fonction_appelee.fonction_appelee == fonctions_existantes.INFORMATION_EN_FONCTION_AUTRE:

            new_dataFrames += exprimer_information_en_fonction_autre(state['dataFrames'], fonction_appelee.args)

        elif fonction_appelee.fonction_appelee == fonctions_existantes.FILTRER_VALEUR:

            new_dataFrames += filtrer_valeur(state['dataFrames'], fonction_appelee.args)

        elif fonction_appelee.fonction_appelee == fonctions_existantes.CREER_GRAPHIQUE:
            
            #new_dataFrames += creer_graphique(state['dataFrames'], fonction_appelee.args, args_restants)
            state['figure'] = creer_graphique(state['dataFrames'], fonction_appelee.args, args_restants)

        elif fonction_appelee.fonction_appelee == fonctions_existantes.FILTRER_COMPARAISON:

            new_dataFrames += filtrer_comparaison(state['dataFrames'], fonction_appelee.args)

        elif fonction_appelee.fonction_appelee == fonctions_existantes.N_PREMIERS:

            new_dataFrames += n_premiers(state['dataFrames'], fonction_appelee.args)


        state['dataFrames'] = new_dataFrames

        message = ""

        for (dataFrame_index) in new_dataFrames:
            message += dataFrame_index.dataFrame.to_html()

        #new_output = {"messages" : [AIMessage(content=message)]}
        print("📦 State après traitement:", list(state.keys()))
        return {
                **state,
                "messages": state["messages"] + [AIMessage(content=message)]
            }
    
    else:
        
        return state