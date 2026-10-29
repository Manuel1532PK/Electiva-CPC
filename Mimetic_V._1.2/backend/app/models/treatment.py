from pydantic import BaseModel, Field
from typing import Optional
from bson import ObjectId


class Medicine(BaseModel):
    name: str
    dosage: Optional[str] = None
    frequency: Optional[str] = None
    duration: Optional[str] = None


class Treatment(BaseModel):
    id: Optional[str] = None
    disease_name: str
    medicines: list[Medicine]
    general_recommendations: Optional[str] = None
    source: Optional[str] = None


class TreatmentInDB(Treatment):
    id: str = Field(default_factory=lambda: str(ObjectId()), alias="_id")
