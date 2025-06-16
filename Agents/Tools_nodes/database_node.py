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
        dfs[es_field] = df
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

from langchain.agents import Tool

es = Elasticsearch(
    ES_HOST,
    basic_auth=(USERNAME, PASSWORD),
    verify_certs=False,
    headers={
        "Accept": "application/vnd.elasticsearch+json; compatible-with=8",
        "Content-Type": "application/vnd.elasticsearch+json; compatible-with=8"
    }
)
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
6. **conversion_cycle** : Indique si nous devons associer un domaine avec des cycles. TRUE si nous voulons et FALSE sinon

Ces valeurs doivent être retournées sous forme d’un objet JSON. Ce code JSON doit être prêt à l'exécution et vérifier toutes les contraintes
d'un fichier JSON
exemple :
{{
    "index": "logstash-huron-k3x8f-202*",
    "fields": ["property.operatingTime", "property.nomProgrammeSelect"],
    "date_from": "now-90d/d",
    "date_to": "now",
    "QUESTION": "Liste les cycles et les programmes associés",
    "conversion_cycle": "TRUE"
}}

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

    input = input[input.find("{"):input.find("}") + 1]

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
    
    dataframes = build_dataframes(all_hits, dict_format_query["fields"])
        
    if dict_format_query["conversion_cycle"] == "TRUE":
        df_tempsCycle = dataframes[dict_format_query["fields"][0]]
        df_programme = dataframes[dict_format_query["fields"][1]]

        # Découpage des cycles en intervalles
        periodes = extraire_intervalles(df_tempsCycle, df_programme, dict_format_query["fields"][1])

        # Affichage final
        df_final = pd.DataFrame.from_dict(periodes, orient="index")
        df_final["start"] = pd.to_datetime(df_final["start"]).dt.strftime('%Y-%m-%d %H:%M:%S')
        df_final["end"] = pd.to_datetime(df_final["end"]).dt.strftime('%Y-%m-%d %H:%M:%S')

        dataframes = df_final
    
    return dataframes
    

import numpy as np
@tool
def getMax(input : str):
    '''Obtenir le maximum d'une suite de nombres. Les nombres sont espacés sous cette forme par exemple : "2 4 5 6"'''
    a = input.split()
    b = list(map(float, a))

    return np.max(np.array(b))

@tool
def eval_function(input : str):
    '''Same as eval function in python. Execute eval({input}). input should be a python instruction or python expression. Consider that there is no defined variables'''

    return eval(input)

tools = [send_query, eval_function]
tool_node = ToolNode(tools)

import OrderState

WELCOME_MSG = (
    "Bonjour ! Je suis votre assistant, comment puis-je vous aider?"
)

from Tools_nodes.database_tools.request_traitement import traitement

from langchain_core.messages.ai import AIMessage

def database_agent(state: OrderState) -> OrderState:
    """The chatbot itself. A wrapper around the model's own chat interface."""

    if state['messages']:
        print(traitement(state['request_call']).to_string())
        new_output = {}
    else:
        new_output = {"messages" : [AIMessage(content=WELCOME_MSG)]}

    return state | new_output

