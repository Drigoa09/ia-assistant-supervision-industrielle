from Tools_nodes.database_tools.request_format import request, Attribut_Principal
import requests
import urllib3
import warnings


import pandas as pd

import os

ES_HOST = os.getenv("ES_HOST")
USERNAME = os.getenv("ES_USER")
PASSWORD = os.getenv("ES_PASSWORD")

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Suppress specific UserWarning message from Pydantic
warnings.filterwarnings(
    "ignore",
    message=r"Pydantic serializer warnings:.*PydanticSerializationUnexpectedValue.*",
    category=UserWarning,
)

def build_dataframes(hits, fields, fields_alias):
    dfs = {}

    i = 0
    for es_field in fields:
        data = [
            (doc["_source"]["@timestamp"], doc["_source"].get(es_field))
            for doc in hits if es_field in doc["_source"]
        ]
        df = pd.DataFrame(data, columns=["timestamp", fields_alias[i]])
        if not df.empty:
            df["timestamp"] = pd.to_datetime(df["timestamp"]).dt.tz_localize(None)
        dfs[es_field] = df

        i += 1
    return dfs

def traitement(request : request):
    all_hits = []
    search_after = None

    date_from = request.periode_requete.date_from
    date_to = request.periode_requete.date_to

    fields = [variables_requete.nom.value for variables_requete in request.variables_requete]
    fields_alias = [variables_requete.alias for variables_requete in request.variables_requete]

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
    
    dataframes = build_dataframes(all_hits, fields, fields_alias)

    return (dataframes, fields_alias)