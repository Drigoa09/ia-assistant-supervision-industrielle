from langchain_mistralai import ChatMistralAI
import os
from dotenv import load_dotenv

#Chargement des variables d'environnement
load_dotenv()

os.environ["MISTRAL_API_KEY"] = os.getenv("MISTRAL_API_KEY")

#Chargement des modeles
model_codestral = ChatMistralAI(model="codestral-latest", temperature = 0)
model_mistral_medium = ChatMistralAI(model="mistral-medium-latest", temperature = 0)
