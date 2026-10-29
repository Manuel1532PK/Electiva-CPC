from pydantic import BaseModel, Field
from typing import Optional
from bson import ObjectId


class Disease(BaseModel):
    id: Optional[str] = None
    name: str
    description: Optional[str] = None
    symptoms: list[str]
    severity: Optional[str] = "moderate"


class DiseaseInDB(Disease):
    id: str = Field(default_factory=lambda: str(ObjectId()), alias="_id")
