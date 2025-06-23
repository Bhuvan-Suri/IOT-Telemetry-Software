import uuid
from typing import Optional
from pydantic import BaseModel, Field

class timeSeriesData(BaseModel):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    temperature: int = Field(...)
    humidity: str = Field(...)
    AQI: int = Field(...)
    time: str = Field(...)
    client_ID: str = Field(...)

    class Config:
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "_id": "066de609-b04a-4b30-b46c-32537c7f1f6e",
                "tempurature": 101,
                "humidity": "12%",
                "AQI": 144,
                "time":"11/11/2025:12:44:44:2142",
                "client_ID":"client 1" 
            }
        }
