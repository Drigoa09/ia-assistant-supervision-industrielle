from typing import Optional
from pydantic import BaseModel, Field

class OutputSchema(BaseModel):
            result: Optional[bool] = Field(default = None, description="Répond uniquement 'true' si la question est liée à Huron, sinon 'false'.")
            description : str = Field(description = "Justification du choix")