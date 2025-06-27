from pydantic import BaseModel, Field
from typing import Optional

class Temps(BaseModel):

    annee : int
    mois : int
    jour : int

fields = {
    "object" : (any, ...),
    "area" : (any, ...),
    "startDate" : (Optional[Temps], Field(default = None, description = "Date de début des positions en format epoch et en milisecondes")),
    "endDate" : (Optional[Temps], Field(default = None, description = "Date de fin des positions en format epoch et en milisecondes"))
}

