from datetime import datetime
from Agents.Tools_nodes.database_node.database_node import DataFrameRole

import pandas as pd

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

    if (args[1] != "-inf" and is_valid_date(inf, "%H:%M:%S")) or (args[2] != "+inf" and is_valid_date(sup, "%H:%M:%S")):
        df = dataFrames[args[0].numero_dataFrame].dataFrame
        
        if inf != -float('inf'):
            df = df[pd.to_datetime(dataFrames_columns, utc=True).dt.time > pd.to_datetime(inf).time()]
        if sup != float('inf'):
            df = df[pd.to_datetime(dataFrames_columns, utc=True).dt.time < pd.to_datetime(sup).time()]
    else:
        df = dataFrames[args[0].numero_dataFrame].dataFrame[float(inf) < dataFrames_columns]
        df = df[dataFrames_columns < float(sup)]

    new_dataFrames.append(DataFrameRole(df, dataFrames[args[0].numero_dataFrame].role + " Filtré par la fonction filtrer_comparaison"))

    return new_dataFrames
