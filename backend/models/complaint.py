
from typing import Optional, List
from pydantic import BaseModel, Field


class Employee(BaseModel):
    employee_id: Optional[str] = None
    name: Optional[str] = None
    email: Optional[str] = None


class Problem(BaseModel):
    description: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None


class Equipment(BaseModel):
    type: Optional[str] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    asset_id: Optional[str] = None
    serial_number: Optional[str] = None


class Location(BaseModel):
    building: Optional[str] = None
    floor: Optional[int] = None

    # Bureau précis
    office: Optional[str] = None

    # Département auquel appartient le lieu
    department: Optional[str] = None

    # Zone générale
    area: Optional[str] = None

    # Localisation précise
    specific_location: Optional[str] = None

    # Pour les lieux communs
    near_department: Optional[str] = None
    near_office: Optional[str] = None
    landmark: Optional[str] = None

    # Pour les toilettes
    restroom_type: Optional[str] = None


class Incident(BaseModel):
    reported_at: Optional[str] = None
    occurred_at: Optional[str] = None
    duration: Optional[str] = None


class Priority(BaseModel):
    level: Optional[str] = None
    reason: Optional[str] = None
    indicators: List[str] = Field(default_factory=list)


class Complaint(BaseModel):
    complaint_id: Optional[str] = None

    employee: Employee = Field(default_factory=Employee)

    problem: Problem = Field(default_factory=Problem)

    equipment: Equipment = Field(default_factory=Equipment)

    location: Location = Field(default_factory=Location)

    incident: Incident = Field(default_factory=Incident)

    priority: Priority = Field(default_factory=Priority)

    status: str = "NEW"