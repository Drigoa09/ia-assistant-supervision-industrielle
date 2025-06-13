from langchain_ollama import ChatOllama
from mistralai import Mistral
from langchain_core.tools import tool
from langchain_mistralai import ChatMistralAI

import os

#model = ChatOllama(model="mistral", temperature = 0)

os.environ["MISTRAL_API_KEY"] = ""
model = "mistral-medium-latest"

model = ChatMistralAI(model=model, temperature = 0)