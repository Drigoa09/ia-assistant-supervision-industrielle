from typing import Annotated, List, TypedDict
from langgraph.graph.message import add_messages
from Tools_nodes.treatment_node.traitement_format import Traitement_Format

from Graph_Agents.ExtractDocsAgent.request_format import request 
from matplotlib.figure import Figure
class OrderState(TypedDict):
    """State representing the customer's order conversation."""

    # The chat conversation. This preserves the conversation history
    # between nodes. The `add_messages` annotation indicates to LangGraph
    # that state is updated by appending returned messages, not replacing
    # them.
    messages: Annotated[list, add_messages]

    #Question posée par l'utilisateur
    question : str

    #Indique l'information cherchée
    information_chercher : str
    #Indique les traitements à effectuer sur l'information cherchée
    traitements : List[str]
    #Indique le traitement actuel sur l'information cherchée
    traitement : str
    i : int

    #Requête obtenue pour en envoyer une à la base de donnée
    request_call : Annotated[request, 'Contient les requêtes']
    # request_call avant l'agent generateur
    request_call_initial: Annotated[request, 'Contient les requêtes avant l\'agent generateur']
    #DataFrame obtenu et traité à partir de la baes de donnée et dont le contenu
    #est envoyé à l'utilisateur
    dataFrames : list

    # Flag indicating that the order is placed and completed.
    finished: bool
    # Traitement formaté pour l'affichage
    traitement_format: Traitement_Format
    # Matplotlib figure to be displayed in the UI
    figure: Figure

    input_tokens : int
    output_tokens : int
    latest_input_tokens: int
    latest_output_tokens: int

    prix_input_tokens : float
    prix_output_tokens : float
    Huron_related: bool