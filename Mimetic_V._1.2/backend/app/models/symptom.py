from pydantic import BaseModel, Field
from typing import Optional
from bson import ObjectId


class Symptom(BaseModel):
    id: Optional[str] = None
    name: str
    description: Optional[str] = None
    category: Optional[str] = None


class SymptomInDB(Symptom):
    id: str = Field(default_factory=lambda: str(ObjectId()), alias="_id")
