import json
from typing import Dict, List
from langgraph.prebuilt import ToolNode
from pydantic import BaseModel
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
from datetime import datetime, timezone

#CONFIGURATION
ES_HOST = ""
USERNAME = ""
PASSWORD = ""
INDEX = "logstash-huron-k3x8f-202*"

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
    for es_field in fields:
        data = [
            (doc["_source"]["@timestamp"], doc["_source"].get(es_field))
            for doc in hits if es_field in doc["_source"]
        ]
        df = pd.DataFrame(data, columns=["timestamp", es_field])
        if not df.empty:
            df["timestamp"] = pd.to_datetime(df["timestamp"]).dt.tz_localize(None)
        dfs[es_field] = df.to_string
    return str(dfs)


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
    

@tool
def getActionsList(input : str) -> str:
    """Renvoie les arguments possible pour envoyer une querry à une base de donnée"""
    return '''Possible arguments pour envoyer une querry :
        cycles_intervals : obtenir les cycles et les intervalles'''

@tool
def sendQuerry(arg : str) -> str:
    """Envoie une requête avec l'argument arg. Il est nécessaire d'entrer le bon argument arg sinon la fonction renvoie null"""
    if arg == '\'cycles_intervals\'':
        return '''Cycle 1 : Utilisation d'un laser pour découper des sushis. Intervalle : 10 s'''
    else:
        return '''Argument incorrect'''
from langchain.agents import Tool

ES_HOST = "https://10.96.1.81:9200"
USERNAME = "elastic"
PASSWORD = "superelsofhell"

es = Elasticsearch(
    ES_HOST,
    basic_auth=(USERNAME, PASSWORD),
    verify_certs=False,
    headers={
        "Accept": "application/vnd.elasticsearch+json; compatible-with=8",
        "Content-Type": "application/vnd.elasticsearch+json; compatible-with=8"
    }
)

from elasticsearch import Elasticsearch
import json

es = Elasticsearch("http://localhost:9200")

def sql_to_es(sql_query: str, size: int = 10) -> list:
    sql_query = sql_query[0:-1]

    try:
        # 1. Traduire SQL en DSL
        translate_resp = es.transport.perform_request(
            method="POST",
            path="/_sql/translate",
            body={"query": sql_query}
        )

        # 2. Exécuter la requête traduite
        es_query = translate_resp["query"]
        index = translate_resp["indices"][0]  # récupère l'index ciblé automatiquement

        search_resp = es.search(index=index, body={"query": es_query}, size=size)

        return [hit["_source"] for hit in search_resp["hits"]["hits"]]

    except Exception as e:
        return [f"Erreur : {str(e)}"]

from langchain_core.tools import tool

@tool
def query_es_from_sql(sql_query: str) -> str:
    """Exécute une requête SQL sur Elasticsearch en la convertissant automatiquement en DSL JSON."""
    results = sql_to_es(sql_query)
    return json.dumps(results, indent=2)

class QueryInput(BaseModel):
    index: str
    fields: List[str]
    date_from: str
    date_to: str
    question: str

import ast

@tool
def send_query(input : str):
    """Tu utilises Elasticsearch comme base de données.
 
🎯 Ta mission est de transformer une question en langage naturel en **4 arguments d'interrogation** utilisables directement dans une requête Elasticsearch :
 
1. **index** : nom de la machine ou du groupe de machines à interroger (ex : `logstash-huron-k3x8f-202*`, `Sigscan`, etc.)
2. **fields** : liste des champs Elasticsearch à extraire (par exemple `["property.operatingTime", "property.nomProgrammeSelect"]`)
3. **date_from** : début de la période, au format Elasticsearch (ex : "now-30d/d" ou "2024-04-16T00:00:00Z"). Pas de fonction dans date_from
4. **date_to** : fin de la période, au format Elasticsearch (ex : "now" ou "2024-04-16T23:59:59Z"). Pas de fonction dans date_to
5. **QUESTION** : Question de l’utilisateur non modifiée

Ces valeurs doivent être retournées sous forme d’un objet JSON

---
 
📏 **Règles fields obligatoires :**
 
- Si la question contient **"cycle"** ou **"programme"** → ajouter `property.operatingTime`, `property.nomProgrammeSelect`
- Si elle contient **"coupe"** ou **"outil"** → ajouter `property.cuttingTime`, `property.nomOutilBroche`
- Si elle contient **"mise sous tension"** ou **"allumée"** → ajouter `property.sumCycleTimeNet`
- Si elle contient **"rendement de coupe"** → ajouter `property.operatingTime`, `property.cuttingTime`
- Si elle contient **"consommation d’électricité"**, **"coût énergétique"**, ou **"puissance"** → ajouter `property.operatingTime`, `property.power_X`, `property.power_Y`, `property.power_Z`, `property.powerSpindle`, `property.power_A`, `property.power_C`
- Si elle contient **"charge de la broche"** ou **"couple"** → ajouter `property.spindlLoad`
- Si elle contient **"température"** ou **"chaleur"** → ajouter `property.tempBrocheExt`
- Si elle contient **"alarme"** ou **"défaut"** → ajouter `property.numDerniereAlarme`
 
---
 
🗂️ **Sélection de l’index :**
- Par défaut → `logstash-huron-k3x8f-202*`
- Si la question mentionne **"sigscan"**, **"bac"**, ou **"géolocalisation"** → `Sigscan`
 
🕓 **Période :**
- Si aucune période n’est mentionnée dans la question → considérer une période par défaut de 90 jours

    """
    dict_format_query = ast.literal_eval(input)

    all_hits = []
    search_after = None
    
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
                                        "gte": dict_format_query["date_from"],
                                        "lte": dict_format_query["date_to"],
                                        "format": "strict_date_optional_time"
                                    }
                                }
                            }
                        ],
                        "should": [{"exists": {"field": field}} for field in dict_format_query["fields"]],
                        "minimum_should_match": 1
                    }
                },
                "_source": ["@timestamp"] + dict_format_query["fields"]
            }
        
        
        if search_after:
            query["search_after"] = [search_after]
        
        response = requests.get(
                f"{ES_HOST}/{dict_format_query["index"]}/_search",
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

    return build_dataframes(all_hits, dict_format_query["fields"])
    

@tool
def getDate(input : str):
    '''Renvoie la date d'aujourd'hui sous format étrange que seul une IA peut gérer'''
    return datetime.now(timezone.utc).isoformat()

class MyArgs(BaseModel):
    index : str
    fields : List[str]
    date_from : str
    date_to : str

tool = Tool.from_function(
    func=send_query,
    name="send_querry",
    description="Tu es un agent spécialisé dans les requêtes ElasticSearch. Utiliser getManFunction pour plus d'informations"
)

tools = [send_query]
tool_node = ToolNode(tools)

# LLM lié aux outils
llm_with_tools = model.bind_tools(tools)

