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

tools = [search_elasticsearch]
tool_node = ToolNode(tools)

# LLM lié aux outils
llm_with_tools = model.bind_tools(tools)
