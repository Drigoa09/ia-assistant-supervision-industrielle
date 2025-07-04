from Tools_nodes.database_node.database_node import DataFrameRole
import pandas as pd

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
