import time
import paho.mqtt.client as paho
import logging
from signal import pause
import ssl


class MqttClient():
    def __init__(
        self,
        chickenHouseName,
        mqttHost,
        onConnectCallBack,
        onDisconnectCallBack,
        onChangeDesiredDoorsStateCallBack,
        mqttPort=1883,
        reconnectWaitTime=5,
        ca_certs=None,
        certfile=None,
        keyfile=None,
        cert_reqs=ssl.CERT_REQUIRED,
        tls_version=ssl.PROTOCOL_TLS,
        ciphers=None):

        self.chickenHouseName = chickenHouseName
        self.mqttHost = mqttHost
        self.mqttPort = mqttPort
        self._onConnectCallBack  = onConnectCallBack
        self._onDisconnectCallBack  = onDisconnectCallBack
        self._onChangeDesiredDoorsStateCallBack  = onChangeDesiredDoorsStateCallBack
        self.reconnectWaitTime = reconnectWaitTime
        self._client = paho.Client(client_id=self.chickenHouseName, clean_session=True)
        # self._client.tls_set(
        #     ca_certs=None,
        #     certfile=None,
        #     keyfile=None,
        #     cert_reqs=ssl.CERT_REQUIRED,
        #     tls_version=ssl.PROTOCOL_TLS,
        #     ciphers=None)
        self._cleanDisconnectFlag=False
        self._client.on_message = self._onChangeDesiredDoorsStateCallBack
        self._client.on_connect = self.__onConnect
        self._client.on_disconnect = self.__onDisconnect
        self._client.enable_logger()
        self.__connect()
        self._client.subscribe(
            topic="chickenrun/%s/+/desired-state" % (self.chickenHouseName),
            qos=2)
        self._client.subscribe(
            topic="chickenrun/global/desired-state",
            qos=2)


    def __del__(self):
        self._cleanDisconnectFlag = True
        self._client.disconnect()
        self._client.loop_stop()


    def __connect(self):
        logging.info("Connecting mqtt client %s to the broker..." %(self.chickenHouseName))
        try:
            rc = self._client.connect(host=self.mqttHost, port=self.mqttPort)
            print("RC="+str(rc))
            self._client.loop_start()
            self._onConnectCallBack()
        except Exception as e:
            logging.error("Mqtt client %s failed to connect to the broker - %s" %(self.chickenHouseName, e))
            self.__reconnect()
            pass


    def __onConnect(self, client, userdata, flags, rc):
        if rc==0:
            logging.info("Mqtt client %s is connected to broker" %(self.chickenHouseName))
            self._client.connected_flag=True
        else:
            """ Bad connection - return codes
            0: Connection successful
            1: Connection refused – incorrect protocol version
            2: Connection refused – invalid client identifier
            3: Connection refused – server unavailable
            4: Connection refused – bad username or password
            5: Connection refused – not authorised
            """
            logging.error("Mqtt client %s failed to connect to the broker (return code: %s)" %(self.chickenHouseName, rc))
            self._client.connected_flag=False
            self._onDisconnectCallBack()
            self.__reconnect()


    def __onDisconnect(self, client, userdata, rc):
        logging.warning("Mqtt client %s is disconnected from the broker" %(self.chickenHouseName))
        self._onDisconnectCallBack()
        if not self._cleanDisconnectFlag:
            self.__reconnect()


    def __reconnect(self):
        logging.warning("Mqtt client %s is trying to reconnect to the broker" %(self.chickenHouseName))
        time.sleep(self.reconnectWaitTime)
        try:
            self._client.loop_stop()
            self.__connect()
        except ConnectionRefusedError:
            self.__reconnect()
            pass


    def publishDoorState(self, doorName, currentState, openDoorSensorState, closedDoorSensorState):
        self._client.publish(
            topic="chickenrun/%s/%s/current-state" % (self.chickenHouseName, doorName),
            payload=currentState.name,
            qos=2,
            retain=False)
        self._client.publish(
            topic="chickenrun/%s/%s/sensors/open" % (self.chickenHouseName, doorName),
            payload=openDoorSensorState,
            qos=2,
            retain=False)
        self._client.publish(
            topic="chickenrun/%s/%s/sensors/closed" % (self.chickenHouseName, doorName),
            payload=closedDoorSensorState,
            qos=2,
            retain=False)


#
#
# test
# logging.basicConfig(level=logging.DEBUG,
#                     format='[%(levelname)s] (%(threadName)-10s) %(message)s',
#                     )
# def on_connect():
#     print("connected")
#
# def on_disconnect():
#     print("disconnected")
#
# def on_message(client, userdata, message):
#     time.sleep(1)
#     print("received message =",str(message.payload.decode("utf-8")))
#
#
# c = MqttClient(
#     chickenHouseName="hello",
#     mqttHost="192.168.86.38",
#     onConnectCallBack=on_connect,
#     onDisconnectCallBack=on_disconnect,
#     onChangeDesiredDoorsStateCallBack=on_message,
#     reconnectWaitTime=5
# )
#
# while True:
#     c.publishDoorState("test", DoorState.Open, 0, 1)
#     time.sleep(1)
#
# pause()
