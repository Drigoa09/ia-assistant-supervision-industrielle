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
from Tools_nodes.database_tools.request_traitement import traitement
from langchain_core.messages.ai import AIMessage
import OrderState

WELCOME_MSG = (
    "Bonjour ! Je suis votre assistant, comment puis-je vous aider?"
)


def database_agent(state: OrderState) -> OrderState:
    """The chatbot itself. A wrapper around the model's own chat interface."""

    if state['messages']:
        print(traitement(state['request_call']).to_string())
        new_output = {}
    else:
        new_output = {"messages" : [AIMessage(content=WELCOME_MSG)]}

    return state | new_output

