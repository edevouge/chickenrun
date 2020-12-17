import time
import logging
import ssl
import sys

from door import Door, DoorState, InvalidDoorState
from housebutton import PressButton
from signals import Signal, SignalState
from mqtt import MqttClient


class ChickenHouse():
    def __init__(self, chickenHouseConfig):
        self.name = None
        self.chickenHouseConfig = chickenHouseConfig
        self._signal = None
        # manual commands
        self._openingButton = None
        self._closingButton = None
        self._doors = []
        self._mqtt = None
        self.loadConfig(chickenHouseConfig)


    def loadConfig(self, chickenHouseConfig):
        #TODO: validate config schema
        self.name = chickenHouseConfig['name']
        self._signal = Signal(
            ledRedGpioPin=chickenHouseConfig['gpioMapping']['ledRedGpioPin'],
            ledGreenGpioPin=chickenHouseConfig['gpioMapping']['ledGreenGpioPin'],
            ledBlueGpioPin=chickenHouseConfig['gpioMapping']['ledBlueGpioPin'],
            buzzerGpioPin=chickenHouseConfig['gpioMapping']['buzzerGpioPin']
        )

        self._openingButton = PressButton(buttonGpioPin=chickenHouseConfig['gpioMapping']['openButtonGpioPin'], onPressedCallback=self.openAllDoors, onHeldCallback=self.hardReset)
        self._closingButton = PressButton(buttonGpioPin=chickenHouseConfig['gpioMapping']['closeButtonGpioPin'], onPressedCallback=self.closeAllDoors, onHeldCallback=self.hardReset)

        for door in chickenHouseConfig['doors']:
            self._doors.append(Door(
                name=door['name'],
                openDoorSensorGpio=door['openDoorSensorGpio'],
                closedDoorSensorGpio=door['closedDoorSensorGpio'],
                motorForwardGpio=door['motorForwardGpio'],
                motorBackwardGpio=door['motorBackwardGpio'],
                changeStateCallback=self._stateChangeCallBack,
                openingTimeout=door['openingTimeout'],
                closingTimeout=door['closingTimeout']
            ))

        self._mqtt = MqttClient(
            chickenHouseName=chickenHouseConfig['name'],
            mqttHost=chickenHouseConfig['mqtt']['mqttHost'],
            onConnectCallBack=self._signal.networkOK,
            onDisconnectCallBack=self._signal.networkError,
            onChangeDesiredDoorsStateCallBack=self.__changeDesiredDoorsState,
            mqttPort=chickenHouseConfig['mqtt']['mqttPort'],
            reconnectWaitTime=chickenHouseConfig['mqtt']['reconnectWaitTime'],
            ca_certs=chickenHouseConfig['mqtt']['ca_certs'],
            certfile=chickenHouseConfig['mqtt']['certfile'],
            keyfile=chickenHouseConfig['mqtt']['keyfile'],
        )


    def openAllDoors(self):
        logging.info("Received order to open all %s doors" % (self.name))
        for door in self._doors:
            door.open()


    def closeAllDoors(self):
        logging.info("Received order to close all %s doors" % (self.name))
        for door in self._doors:
            door.close()


    def hardReset(self):
        logging.info("Received a hard reset signal")
        for door in self._doors:
            door.initialize()
        self._mqtt.__del__()
        self._mqtt = MqttClient(
            chickenHouseName=self.chickenHouseConfig['name'],
            mqttHost=self.chickenHouseConfig['mqtt']['mqttHost'],
            onConnectCallBack=self._signal.networkOK,
            onDisconnectCallBack=self._signal.networkError,
            onChangeDesiredDoorsStateCallBack=self.__changeDesiredDoorsState,
            mqttPort=self.chickenHouseConfig['mqtt']['mqttPort'],
            reconnectWaitTime=self.chickenHouseConfig['mqtt']['reconnectWaitTime'],
            ca_certs=self.chickenHouseConfig['mqtt']['ca_certs'],
            certfile=self.chickenHouseConfig['mqtt']['certfile'],
            keyfile=self.chickenHouseConfig['mqtt']['keyfile'],
        )


    def __changeDesiredDoorsState(self, client, userdata, message):
        for door in self._doors:
            try:
                door.desiredState = DoorState[str(message.payload.decode("utf-8"))]
            except InvalidDoorState as e:
                logging.error("Invalid door state: %s" %(message.payload.decode("utf-8")))
                pass


    def _stateChangeCallBack(self, state):
        logging.info("Current state changer to: %s" %(str(state.name)))
        if state == DoorState.Opening or state == DoorState.Closing:
            self._signal.state = SignalState.DoorOperating
        elif state == DoorState.Closed or state == DoorState.Open:
            self._signal.state = SignalState.UpAndRuning
        elif state == DoorState.Error:
            self._signal.state = SignalState.DoorTimeoutError
        elif state == DoorState.Initialize:
            self._signal.state = SignalState.Initialize
