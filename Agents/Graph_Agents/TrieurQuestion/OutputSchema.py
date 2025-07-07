from typing import Optional
from pydantic import BaseModel, Field

class OutputSchema(BaseModel):
            result: bool = Field(description="Répond uniquement 'true' si la question est liée à Huron, sinon 'false'.")