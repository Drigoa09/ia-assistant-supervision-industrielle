from pydantic import BaseModel, Field
from typing import Optional

class Temps(BaseModel):

    annee : int = Field(default=None, description = "Année")
    mois : int = Field(default=None, description = "Mois")
    jour : int = Field(default=None, description = "Jour")

fields = {
    "object" : (any, ...),
    "area" : (any, ...),
    "startDate" : (Optional[Temps], Field(default = None, description = "Date de début des positions")),
    "endDate" : (Optional[Temps], Field(default = None, description = "Date de fin des positions"))
}

