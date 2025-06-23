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

NOTE:
the api only has Create and Read function (assumption being that IOT devices do not need to edit or delete any files after sending them to database) 

