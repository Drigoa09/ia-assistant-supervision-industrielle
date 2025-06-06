from langgraph.prebuilt import ToolNode
from model import model

from langchain_core.tools import tool

from elasticsearch import Elasticsearch
import os

es = Elasticsearch(
    os.getenv("ES_HOST"),
    basic_auth=(os.getenv("ES_USER"), os.getenv("ES_PASSWORD")),
)

@tool
def search_elasticsearch(query: dict) -> list:
    """
    Reçoit une requête Elasticsearch (au format dict) et retourne les documents.
    """
    response = es.search(
        index=os.getenv("ES_INDEX"),
        query=query,
        size=10
    )
    
    return [hit["_source"] for hit in response["hits"]["hits"]]

#---------------------------------------------------------------------------------------------

import pandas as pd
import requests
import urllib3
from requests.auth import HTTPBasicAuth
from datetime import datetime

#CONFIGURATION

FIELDS = {
    "programme": "property.nomProgrammeSelect",
    "tempsCycle": "property.operatingTime"
}

DATE_FROM = "now-90d/d"
DATE_TO = "now"
PAGE_SIZE = 1000

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Requête Elastic
def fetch_all_hits(es_host, index, field_list, date_from, date_to, auth, page_size=1000):
    all_hits = []
    search_after = None

    while True:
        query = {
            "size": page_size,
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
                    "should": [{"exists": {"field": field}} for field in field_list],
                    "minimum_should_match": 1
                }
            },
            "_source": ["@timestamp"] + field_list
        }

        if search_after:
            query["search_after"] = [search_after]

        response = requests.get(
            f"{es_host}/{index}/_search",
            auth=auth,
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

    return all_hits


# Construction DataFrame
def build_dataframes(hits, fields):
    dfs = {}
    for label, es_field in fields.items():
        data = [
            (doc["_source"]["@timestamp"], doc["_source"].get(es_field))
            for doc in hits if es_field in doc["_source"]
        ]
        df = pd.DataFrame(data, columns=["timestamp", label])
        if not df.empty:
            df["timestamp"] = pd.to_datetime(df["timestamp"]).dt.tz_localize(None)
        dfs[label] = df
    return dfs


# Extraire les intervalles de cycle
def extraire_intervalles(df_source, df_contexte, variable_contexte, seuil_pause=5):
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
            "programme": programme
        }

    return periodes


# Exécution principale

@tool
def tool_cycle(date_from : str, date_to : str) -> str:
    '''Liste les cycles et les programmes associés entre date_from et date_to. date_from et date_to sont des dates données au format ISO 8601'''

    print(date_from, date_to)

    auth = HTTPBasicAuth(USERNAME, PASSWORD)
    es_fields = list(FIELDS.values())

    hits = fetch_all_hits(ES_HOST, INDEX, es_fields, date_from, date_to, auth, PAGE_SIZE)
    print(f" {len(hits)} documents récupérés\n")

    # Extraction des DataFrames utilisés
    dataframes = build_dataframes(hits, FIELDS)
    df_tempsCycle = dataframes.get("tempsCycle")
    df_programme = dataframes.get("programme")

    # Vérification
    if df_tempsCycle is None or df_tempsCycle.empty:
        return "Aucun cycle détecté."
    elif df_programme is None or df_programme.empty:
        return "Aucun programme détecté."
    else:
        # Découpage des cycles en intervalles
        periodes = extraire_intervalles(df_tempsCycle, df_programme, "programme")

        # Affichage final
        df_final = pd.DataFrame.from_dict(periodes, orient="index")
        df_final["start"] = pd.to_datetime(df_final["start"]).dt.strftime('%Y-%m-%d %H:%M:%S')
        df_final["end"] = pd.to_datetime(df_final["end"]).dt.strftime('%Y-%m-%d %H:%M:%S')

        df_final.drop(["temps(s)"], axis=1)
        print("Intervalles de cycles et programmes associés :")
        print(df_final.to_string(index=True))
        return {"colonnes" : df_final.columns, "donnees" : df_final.to_dict()}
    

tools = [tool_cycle]
tool_node = ToolNode(tools)

# LLM lié aux outils
llm_with_tools = model.bind_tools(tools)

