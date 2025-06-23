# IOT Telemetry Software
This is a telemetry application for IOT devices that uploads IOT software to a cloud database

File info:
DirectToServerClientCode-
This file utilises the Telemetry SDK to send generated JSON files to the database via the RESTful API It generates JSON file using pythons inbuilt random library. For actual applications generate the JSON files using sensors
.env-
This file stores the connection string for the mongodb database along with the name of the database being written to, update the string and name in accordance to your own database
routes-
This file defines the GET, GET(ID), and POST calls that can be made using the RESTful API, this file should be changed in accordance to the name of your database along with the name of the class defined in the models.py file
models-
Stores the acceptable JSON format for the API, change this as per the format you wish to use
Telemetry-
This is the SDK that can be used by the client to contact the RESTful API, no changes needed
Telemetry_Config-
This is the config for the SDK that should be edited in accordance to the url and client id of the RESTFUL api and client respectively

Usage:
To run the api use the following commands:
python3 -m venv env-pymongo-fastapi-crud
source env-pymongo-fastapi-crud/bin/activate
then navigate to the directory where the files are stored in my case it is:
cd desktop
cd workspace
cd code
cd pymongo-fastapi-create-read

Then start the api:
python -m uvicorn main:app --reload

Following this navigate to the directory where the DirectToServerClientCode.py file is stored, in my case using the following commands:
cd desktop
cd workspace
cd code

then run the code:
python3 DirectToServerClientCode.py

this should add one piece of time series data to your database

NOTE:
the api only has Create and Read function (assumption being that IOT devices do not need to edit or delete any files after sending them to database) 

