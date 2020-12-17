import time
import paho.mqtt.client as paho
from enum import Enum

MQTT_HOST = "10.10.0.1"
FARM_ID = "Ferme-Nostang"
CHICKEN_HOUSE_ID = "cabane-1"


class DoorState(Enum):
    Initialize = 0
    Opening = 1
    Open = 2
    Closing = 3
    Closed = 4
    Error = 5



def on_message(client, userdata, message):
    time.sleep(1)
    print("received message =",str(message.payload.decode("utf-8")))


client = paho.Client(CHICKEN_HOUSE_ID)
client.on_message=on_message
client.connect(MQTT_HOST)
client.loop_start()

time.sleep(2)
print("publishing ")
client.publish(
    topic="chickenrun/global/desired-state",
    payload=DoorState.Open.name,
    qos=2,
    retain=True)
time.sleep(4)
client.subscribe(
    topic="chickenrun/global/desired-state",
    qos=2)
time.sleep(100)
client.disconnect()
client.loop_stop()
