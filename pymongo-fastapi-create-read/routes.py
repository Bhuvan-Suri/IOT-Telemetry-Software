from fastapi import APIRouter, Body, Request, Response, HTTPException, status
from fastapi.encoders import jsonable_encoder
from typing import List

from models import timeSeriesData

router = APIRouter()

@router.post("/", response_description="Create a new time series data", status_code=status.HTTP_201_CREATED, response_model=timeSeriesData)
def create_book(request: Request, TimeSeriesData: timeSeriesData = Body(...)):
    TimeSeriesData = jsonable_encoder(TimeSeriesData)
    new_timeSeriesData = request.app.database["timeSeriesData"].insert_one(TimeSeriesData)
    created_timeSeriesData = request.app.database["timeSeriesData"].find_one(
        {"_id": new_timeSeriesData.inserted_id}
    )

    return created_timeSeriesData


@router.get("/", response_description="List all timeSeriesData", response_model=List[timeSeriesData])
def list_books(request: Request):
    TimeSeriesData = list(request.app.database["timeSeriesData"].find(limit=100))
    return TimeSeriesData

@router.get("/{id}", response_description="Get a single timeSeriesData by id", response_model=timeSeriesData)
def find_timeSeriesData(id: str, request: Request):
    if (timeSeriesData := request.app.database["timeSeriesData"].find_one({"_id": id})) is not None:
        return timeSeriesData
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"timeSeriesData with ID {id} not found")
