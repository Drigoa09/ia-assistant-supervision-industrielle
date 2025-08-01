import os

from langgraph.graph import StateGraph, START, MessagesState

from Graph_Agents.human_node import human_node, maybe_exit_human_node
from Graph_Agents.CreateurTache.CreateurTache import CreateurTache
from Graph_Agents.CreateurTache.Separation import Separation
from Graph_Agents.Sigscan.Agents.Agents.formaliseur_requete import Formalisateur_requete
from Graph_Agents.Sigscan.Agents.Agents.prompt import PROMPT
from Graph_Agents.Sigscan.BDD.interactionBdd import InteractionBdd
from Graph_Agents.Sigscan.Requetes.Requetes.objects import Objet
from Graph_Agents.Sigscan.Requetes.Requetes.areas import Area
from Tools_nodes.database_node.database_node import database_agent
from Tools_nodes.continuer_node.continuer_node import Continuer_node
from Graph_Agents.TreatmentAgent.treatmentAgent import TreatmentAgent
from Graph_Agents.TreatmentAgent.prompt_treatmentAgent import AGENT_GENERATION_SYSINT, EXEMPLES
from Tools_nodes.treatment_node.treatment_node import treatment_node
from Graph_Agents.TrieurQuestion.Trieur_question_agent import Trieur_question_agent
from Tools_nodes.trieur_node.trieur_node import Trieur_node
from Graph_Agents.TrieurQuestion.OutputSchema import OutputSchema
from Graph_Agents.ExtractDocsAgent.Extract_docs_agent import Extract_docs_agent

from Graph_Agents.GenerateurAgent.generateur_agent import Generateur_agent, Choix
from Tools_nodes.generateur_node.generateur_node import generateur_node

from Tools_nodes.treatment_node.traitement_format import fonction

from OrderState import OrderState

createurTache = CreateurTache(Separation)
continuer_node = Continuer_node()
generer_reponse = Generateur_agent(Choix)
treatmentAgent = TreatmentAgent(fonction, AGENT_GENERATION_SYSINT, EXEMPLES)
extract_doc_agent = Extract_docs_agent()
trieur_question = Trieur_question_agent(OutputSchema)
trieur_node = Trieur_node()
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGSMITH_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGCHAIN_API_KEY"] = "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" #Enlever ensuite
os.environ["LANGCHAIN_PROJECT"] = "My_project"
formalisateur_requete = Formalisateur_requete(prompt_debut=PROMPT, objets=Objet, areas=Area)
interactionBdd = InteractionBdd()
# Start building a new graph.
graph_builder = StateGraph(OrderState)

# Add the chatbot and human nodes to the app graph.
#graph_builder.add_node("chatbot", chatbot_with_welcome_msg)
graph_builder.add_node("Humain", human_node)
graph_builder.add_node("Trieur de questions", trieur_question.interaction)
graph_builder.add_node("Créateur de tâches", createurTache.interaction)
graph_builder.add_node("Formulateur de demandes d'informations", extract_doc_agent.interaction)
graph_builder.add_node("Executeur de demandes d'informations", database_agent)
graph_builder.add_node("Formulateur de requêtes de traitement", treatmentAgent.interaction)
graph_builder.add_node("Indicateur de l'existance de traitements supplémentaires", continuer_node.continuer_node)
graph_builder.add_node("Executeur de requêtes de traitement", treatment_node)

graph_builder.add_node("Générateur de réponse", generer_reponse.interaction)
graph_builder.add_node("Application du générateur", generateur_node)

graph_builder.add_node("Formalisateur de requête", formalisateur_requete.formaliser_requete)
graph_builder.add_node("Interaction à la base de donnée", interactionBdd.interactionBdd)

# The chatbot will always go to the human next.

graph_builder.add_conditional_edges("Humain", maybe_exit_human_node)
graph_builder.add_conditional_edges("Indicateur de l'existance de traitements supplémentaires", continuer_node.maybe_route_to_treatment)
graph_builder.add_conditional_edges("Trieur de questions", trieur_node.sigscan_or_huron)
# pour sigscan
graph_builder.add_edge("Formalisateur de requête", "Interaction à la base de donnée")
graph_builder.add_edge("Interaction à la base de donnée", "Humain")
#pour huron
graph_builder.add_edge("Créateur de tâches", "Formulateur de demandes d'informations")
graph_builder.add_edge("Formulateur de demandes d'informations", "Executeur de demandes d'informations")
graph_builder.add_edge("Executeur de demandes d'informations", "Indicateur de l'existance de traitements supplémentaires")
graph_builder.add_edge("Formulateur de requêtes de traitement", "Executeur de requêtes de traitement")
graph_builder.add_edge("Executeur de requêtes de traitement", "Indicateur de l'existance de traitements supplémentaires")

graph_builder.add_edge("Générateur de réponse", "Application du générateur")
graph_builder.add_edge("Application du générateur", "Humain")

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
