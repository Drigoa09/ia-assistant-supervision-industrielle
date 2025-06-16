from Tools_nodes.database_tools.request_format import request
import requests
import urllib3

import pandas as pd

import os

ES_HOST = os.getenv("ES_HOST")
USERNAME = os.getenv("ES_USER")
PASSWORD = os.getenv("ES_PASSWORD")

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def build_dataframes(hits, fields):
    dfs = {}
    for es_field in fields:
        data = [
            (doc["_source"]["@timestamp"], doc["_source"].get(es_field))
            for doc in hits if es_field in doc["_source"]
        ]
        df = pd.DataFrame(data, columns=["timestamp", es_field])
        if not df.empty:
            df["timestamp"] = pd.to_datetime(df["timestamp"]).dt.tz_localize(None)
        dfs[es_field] = df
    return dfs

# Extraire les intervalles de cycle
def extraire_intervalles(df_source, df_contexte, variable_contexte, nom_second, seuil_pause=5):
    df_source = df_source.copy()
    df_source["time_diff"] = df_source["timestamp"].diff().dt.total_seconds()
    split_indices = df_source.index[df_source["time_diff"] > seuil_pause].tolist()
    sub_tables = [df_source.iloc[start:end] for start, end in zip([0]+split_indices, split_indices+[len(df_source)]) if end - start > 1]
    df_source.drop(columns="time_diff", inplace=True)

    periodes = {}
    for i, table in enumerate(sub_tables, 1):
        start, end = table["timestamp"].iloc[0], table["timestamp"].iloc[-1]
        duration = (end - start).total_seconds()
        matching = df_contexte[df_contexte["timestamp"] < start]
        programme = str(matching.iloc[-1][variable_contexte]) if not matching.empty else None
        periodes[f"interval_{i}"] = {
            "start": start,
            "end": end,
            "temps(s)": round(duration, 1),
            nom_second: programme
        }

    return periodes

def traitement(request : request):
    all_hits = []
    search_after = None

    date_from = request.periode_requete.date_from
    date_to = request.periode_requete.date_to
    fields = [request.variable_principale_requete.nom.value] + [variable_contexte_requete.nom.value for variable_contexte_requete in request.variables_contextes_requete]

    index = request.machine_request.value
    
    while True:
        query = {
                "size": 1000,
                "sort": [{"@timestamp": "asc"}],  
                "query": {
                    "bool": {
                        "filter": [
                            {
                                "range": {
                                    "@timestamp": {
                                        "gte": date_from,
                                        "lte": date_to,
                                        "format": "strict_date_optional_time"
                                    }
                                }
                            }
                        ],
                        "should": [{"exists": {"field": field}} for field in fields],
                        "minimum_should_match": 1
                    }
                },
                "_source": ["@timestamp"] + fields
            }
        
        
        if search_after:
            query["search_after"] = [search_after]
        
        response = requests.get(
                f"{ES_HOST}/{index}/_search",
                auth=(USERNAME, PASSWORD),
                headers={"Content-Type": "application/json"},
                json=query,
                verify=False
            )

        
        if response.status_code != 200:
            raise RuntimeError(f"Erreur {response.status_code} - {response.text}")

        hits = response.json()["hits"]["hits"]
        if not hits:
            break

        all_hits.extend(hits)
        search_after = hits[-1]["sort"][0]
    
    dataframes = build_dataframes(all_hits, fields)
        
    
    df_tempsCycle = dataframes[request.variable_principale_requete.nom.value]
    df_programme = dataframes[request.variables_contextes_requete[0].nom.value]

    # Découpage des cycles en intervalles
    periodes = extraire_intervalles(df_tempsCycle, df_programme, request.variables_contextes_requete[0].nom.value, request.variables_contextes_requete[0].alias)

    # Affichage final
    df_final = pd.DataFrame.from_dict(periodes, orient="index")
    df_final["start"] = pd.to_datetime(df_final["start"]).dt.strftime('%Y-%m-%d %H:%M:%S')
    df_final["end"] = pd.to_datetime(df_final["end"]).dt.strftime('%Y-%m-%d %H:%M:%S')

    dataframes = df_final
    
    return dataframes