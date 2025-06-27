from dotenv import load_dotenv

#Chargement des variables d'environnement
load_dotenv()

from langgraph.graph import StateGraph, START
import os
from State import State

from Agents.formaliseur_requete import Formalisateur_requete
from Human.human import Human
from InteractionBdd.interactionBdd import InteractionBdd

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGSMITH_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY") #Enlever ensuite
os.environ["LANGCHAIN_PROJECT"] = "My_project"

formalisateur_requete = Formalisateur_requete(None, None)
human = Human("Antoine Drigo")
interactionBdd = InteractionBdd()

# Start building a new graph.
graph_builder = StateGraph(State)

# Add the chatbot and human nodes to the app graph.
#graph_builder.add_node("chatbot", chatbot_with_welcome_msg)
graph_builder.add_node("Humain", human.demander_question)
graph_builder.add_node("Formalisateur de requête", formalisateur_requete.formaliser_requete)
graph_builder.add_node("Interaction à la base de donnée", interactionBdd.interactionBdd)

# The chatbot will always go to the human next.

graph_builder.add_conditional_edges("Humain", human.maybe_exit_with_human_node)

graph_builder.add_edge("Formalisateur de requête", "Interaction à la base de donnée")
graph_builder.add_edge("Interaction à la base de donnée", "Humain")

# Start with the chatbot again.
graph_builder.add_edge(START, "Humain")

chat_with_human_graph = graph_builder.compile()

# The default recursion limit for traversing nodes is 25 - setting it higher means
# you can try a more complex order with multiple steps and round-trips (and you
# can chat for longer!)
config = {"recursion_limit": 100}

# Remember that this will loop forever, unless you input `q`, `quit` or one of the
# other exit terms defined in `human_node`.
# Uncomment this line to execute the graph:
#state = chat_with_human_graph.invoke({"messages": []}, config)
if __name__ == "__main__":
    # Pour tester le graphe manuellement (utile en dev)
    state = {"messages": []}
    result = chat_with_human_graph.invoke(state, config={"recursion_limit": 100})
# Things to try:
#  - Just chat! There's no ordering or menu yet.
#  - 'q' to exit.

'''
from langchain_core.runnables.graph import MermaidDrawMethod
from IPython.display import Image, display

Image(chat_with_human_graph.get_graph().draw_mermaid_png())
'''
