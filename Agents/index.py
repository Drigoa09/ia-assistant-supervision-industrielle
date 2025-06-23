import os

from langgraph.graph import StateGraph, START, MessagesState

from Graph_Agents.human_node import human_node, maybe_exit_human_node
from Graph_Agents.CreateurTache import createur_tache
from Graph_Agents.Extract_docs_agent import extract_docs_agent
from Tools_nodes.database_node import database_agent
from Tools_nodes.continuer_node import continuer_node, maybe_route_to_treatment
from Graph_Agents.treatment_agent import treatment_agent
from Tools_nodes.treatment_node import treatment_node

from OrderState import OrderState


os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGSMITH_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGCHAIN_API_KEY"] = "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" #Enlever ensuite
os.environ["LANGCHAIN_PROJECT"] = "My_project"

# Start building a new graph.
graph_builder = StateGraph(OrderState)

# Add the chatbot and human nodes to the app graph.
#graph_builder.add_node("chatbot", chatbot_with_welcome_msg)
graph_builder.add_node("Humain", human_node)
graph_builder.add_node("Créateur de tâches", createur_tache)
graph_builder.add_node("Formulateur de demandes d'informations", extract_docs_agent)
graph_builder.add_node("Executeur de demandes d'informations", database_agent)
graph_builder.add_node("Formulateur de requêtes de traitement", treatment_agent)
graph_builder.add_node("Indicateur de l'existance de traitements supplémentaires", continuer_node)
graph_builder.add_node("Executeur de requêtes de traitement", treatment_node)

# The chatbot will always go to the human next.

graph_builder.add_conditional_edges("Humain", maybe_exit_human_node)
graph_builder.add_conditional_edges("Indicateur de l'existance de traitements supplémentaires", maybe_route_to_treatment)

graph_builder.add_edge("Créateur de tâches", "Formulateur de demandes d'informations")
graph_builder.add_edge("Formulateur de demandes d'informations", "Executeur de demandes d'informations")
graph_builder.add_edge("Executeur de demandes d'informations", "Indicateur de l'existance de traitements supplémentaires")
graph_builder.add_edge("Formulateur de requêtes de traitement", "Executeur de requêtes de traitement")
graph_builder.add_edge("Executeur de requêtes de traitement", "Indicateur de l'existance de traitements supplémentaires")

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
