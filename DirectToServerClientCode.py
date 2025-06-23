import random
from SDK import Telemetry

#defining a function to make a json and return the json as a string
def makeSensorValues():
    random.seed()
    sensorValues = {
        'temperature':int(random.randrange(1,55)),
        'humidity':str(random.randrange(1,100))+'%',
        'AQI':int(random.randrange(0,450))
    }
    return sensorValues


Telemetry.post(makeSensorValues())
