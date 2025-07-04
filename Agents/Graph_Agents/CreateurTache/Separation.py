from typing import List
from pydantic import BaseModel, Field
from typing import Optional, List

#Forme de la réponse voulue donnée par l'agent
class Separation(BaseModel):
    """Sépare un texte pour en obtenir l'information à chercher et le traitement fait sur l'information.
    Les données contenues dans les attributs doivent être des phrases
    """

    INFORMATION_CHERCHER : str = Field(description = "Information recherchée dans la base de donnée. Exprimé sous forme d'un ordre.")
    TRAITEMENT : Optional[List[str]] = Field(default= None, description = "Traitements faits sur les informations de la base de donnée déduit à partir de la question. Exprimé sous forme d'un ordre")
