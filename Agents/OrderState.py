from typing import Annotated, List, TypedDict
from langgraph.graph.message import add_messages

from Tools_nodes.database_tools.request_format import request 

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

    #DataFrame obtenu et traité à partir de la baes de donnée et dont le contenu
    #est envoyé à l'utilisateur
    dataFrames : list
    #Contient les colonnes de la dataFrame
    dataFrames_columns : list[str]
    dataFrames_role : list[str]

    # Flag indicating that the order is placed and completed.
    finished: bool
