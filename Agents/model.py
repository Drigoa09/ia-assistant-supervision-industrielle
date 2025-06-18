from langchain_ollama import ChatOllama
from mistralai import Mistral
from langchain_core.tools import tool
from langchain_mistralai import ChatMistralAI

import os

#model = ChatOllama(model="mistral", temperature = 0)

os.environ["MISTRAL_API_KEY"] = os.getenv("MISTRAL_API_KEY")

model_codestral = ChatMistralAI(model="codestral-latest", temperature = 0)
model_mistral_medium = ChatMistralAI(model="mistral-medium-latest", temperature = 0)