from pydantic import BaseModel, Field
from typing import Optional
from bson import ObjectId
from datetime import datetime


class Hospital(BaseModel):
    id: Optional[str] = None
    name: str
    code: str
    address: str = ""
    phone: str = ""
    email: str = ""
    active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)


class HospitalInDB(Hospital):
    id: str = Field(default_factory=lambda: str(ObjectId()), alias="_id")


class HospitalCreate(BaseModel):
    name: str
    code: str
    address: str = ""
    phone: str = ""
    email: str = ""


class HospitalUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    active: Optional[bool] = None


class HospitalOut(BaseModel):
    id: str
    name: str
    code: str
    address: str = ""
    phone: str = ""
    email: str = ""
    active: bool = True
    created_at: datetime