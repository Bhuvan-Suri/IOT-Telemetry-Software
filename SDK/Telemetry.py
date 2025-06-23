import datetime
import requests
from jproperties import Properties

config = Properties()
with open('/Users/bhuvansuri/Desktop/workspace/code/SDK/Telemetry_Config.properties', 'rb') as config_file:
    config.load(config_file)

clientID = config.get("clientID").data
url = config.get("url").data

def post(sensorValues):
    sensorValues["time"] = str(datetime.datetime.now())
    sensorValues["client_ID"] = clientID
    requests.post(url, json=sensorValues)
    print(sensorValues)