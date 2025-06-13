from dotenv import load_dotenv

import os

load_dotenv()

from langgraph.graph import StateGraph, START

from Graph_Agents.AgentGeneration import chatbot_with_welcome_msg, maybe_route_to_extract_docs
from Graph_Agents.human_node import human_node, maybe_exit_human_node
from Graph_Agents.Extract_docs_agent import extract_docs_agent, maybe_route_to_database
from Graph_Agents.Evaluation_docs_agent import evaluation_docs_agent
from Graph_Agents.generateurReponse import generer_reponse
from Tools_nodes.message_erreur import afficher_erreur
from Tools_nodes.database_node import tool_node

from OrderState import OrderState


os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGSMITH_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGCHAIN_API_KEY"] = "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" #Enlever ensuite
os.environ["LANGCHAIN_PROJECT"] = "My_project"

# Start building a new graph.
graph_builder = StateGraph(OrderState)

# Add the chatbot and human nodes to the app graph.
#graph_builder.add_node("chatbot", chatbot_with_welcome_msg)
graph_builder.add_node("human", human_node)
graph_builder.add_node("extract_docs", extract_docs_agent)
graph_builder.add_node("query_elasticsearch", tool_node)
#graph_builder.add_node("evaluation_doc_agent", evaluation_docs_agent)
#graph_builder.add_node("erreur", afficher_erreur)
graph_builder.add_node("generer_reponse", generer_reponse)

# The chatbot will always go to the human next.

#graph_builder.add_conditional_edges("chatbot", maybe_route_to_database)

graph_builder.add_conditional_edges("human", maybe_exit_human_node)

#graph_builder.add_conditional_edges("chatbot", maybe_route_to_extract_docs)
graph_builder.add_conditional_edges("extract_docs", maybe_route_to_database)
graph_builder.add_edge("query_elasticsearch", "extract_docs")
#graph_builder.add_edge("erreur", "human")
#graph_builder.add_edge("evaluation_doc_agent", "human")
graph_builder.add_edge("generer_reponse", "human")

# Start with the chatbot again.
graph_builder.add_edge(START, "generer_reponse")

chat_with_human_graph = graph_builder.compile()

# The default recursion limit for traversing nodes is 25 - setting it higher means
# you can try a more complex order with multiple steps and round-trips (and you
# can chat for longer!)
config = {"recursion_limit": 100}

# Remember that this will loop forever, unless you input `q`, `quit` or one of the
# other exit terms defined in `human_node`.
# Uncomment this line to execute the graph:
# state = chat_with_human_graph.invoke({"messages": []}, config) # Commented out for app.py integration

# Things to try:
#  - Just chat! There's no ordering or menu yet.
#  - 'q' to exit.
'''
from langchain_core.runnables.graph import MermaidDrawMethod
from IPython.display import Image, display

# Image(chat_with_human_graph.get_graph().draw_mermaid_png()) # Commented out for app.py integration
'''

