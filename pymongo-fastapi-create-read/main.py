from fastapi import FastAPI
from dotenv import dotenv_values
from pymongo import MongoClient
from routes import router as timeSeriesSensorData_router

config = dotenv_values(".env")

app = FastAPI()

@app.on_event("startup")
def startup_db_client():
    app.mongodb_client = MongoClient(config["ATLAS_URI"])
    app.database = app.mongodb_client[config["DB_NAME"]]

@app.on_event("shutdown")
def shutdown_db_client():
    app.mongodb_client.close()

app.include_router(timeSeriesSensorData_router, tags=["timeSeriesSensorData"], prefix="/timeSeriesSensorData")

