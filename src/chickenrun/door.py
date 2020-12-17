import logging
from enum import Enum
from doormotor import DoorMotor, RunMotorTimeoutException
import threading
import time


class InvalidDoorState(Exception):
    pass


class DoorState(Enum):
    Initialize = 0
    Opening = 1
    Open = 2
    Closing = 3
    Closed = 4
    Error = 5


class Door():
    def __init__(self, name, openDoorSensorGpio, closedDoorSensorGpio, motorForwardGpio, motorBackwardGpio, changeStateCallback=None, openingTimeout=10, closingTimeout=8):
        self.name = name

        self._doorMotor = DoorMotor(
            motorForwardChannel=motorForwardGpio,
            motorBackwardChannel=motorBackwardGpio,
            forwardLimitSensorChannel=openDoorSensorGpio,
            backwardLimitSensorChannel=closedDoorSensorGpio,
            forwardTimeout=openingTimeout,
            backwardTimeout=closingTimeout)

        self.changeStateCallback = changeStateCallback

        self._desiredState = DoorState.Initialize
        self._currentState = DoorState.Initialize

        self._runEvent = threading.Event()
        self._runEvent.set()
        self._stateReconciliationLoopThread = threading.Thread(
            target = self.__desiredStateSupervisor
        )
        self._stateReconciliationLoopThread.start()


    def __del__(self):
        self._doorMotor.__del__()
        self._runEvent.clear()
        self._stateReconciliationLoopThread.join()

    @property
    def openDoorSensorState(self):
        return self._doorMotor.forwardLimitSensorState

    @property
    def closedDoorSensorState(self):
        return self._doorMotor.backwardLimitSensorState

    @property
    def currentState(self):
        return self._currentState

    @property
    def desiredState(self):
        return self._desiredState

    @desiredState.setter
    def desiredState(self, desiredState):
        if isinstance(desiredState, DoorState):
            self._desiredState = desiredState
        else:
            raise InvalidDoorState()

    def __onStateChange(self):
        if callable(self.changeStateCallback):
            self.changeStateCallback(self._currentState)

    def __setCurrentState(self, state):
        if isinstance(state, DoorState):
            self._currentState = state
            self.__onStateChange()
        else:
            raise InvalidDoorState()


    def __desiredStateSupervisor(self, updateFrequency=0.1):
        logging.debug("Starting StateSupervisor")
        while self._runEvent.is_set():
            if self._desiredState != self._currentState:
                if self._desiredState == DoorState.Open and self._currentState in (DoorState.Initialize, DoorState.Closed, DoorState.Closing):
                    try:
                        self.__setCurrentState(DoorState.Opening)
                        self._doorMotor.forward()
                        if self.openDoorSensorState:
                            self.__setCurrentState(DoorState.Open)
                        else:
                            self.__setCurrentState(DoorState.Error)
                    except RunMotorTimeoutException as e:
                        logging.error("Door %s is experimenting timeout error trying to open" % (self.name) )
                        self.__setCurrentState(DoorState.Error)
                        pass
                elif self._desiredState == DoorState.Closed and self._currentState in (DoorState.Initialize, DoorState.Open, DoorState.Opening):
                    try:
                        self.__setCurrentState(DoorState.Closing)
                        self._doorMotor.backward()
                        if self.closedDoorSensorState:
                            self.__setCurrentState(DoorState.Closed)
                        else:
                            self.__setCurrentState(DoorState.Error)
                    except RunMotorTimeoutException as e:
                        logging.error("Door %s is experimenting timeout error trying to open" % (self.name) )
                        self.__setCurrentState(DoorState.Error)
                        pass
                elif self._desiredState == DoorState.Initialize:
                    self.__setCurrentState(DoorState.Initialize)

                # Do nothing if currentState in (DoorState.Error, DoorState.Opening, DoorState.Closing)

            # Sleep time before next reconciliation loop
            time.sleep(updateFrequency)


    def open(self):
        self._desiredState = DoorState.Open


    def close(self):
        self._desiredState = DoorState.Closed


    def initialize(self):
        self._desiredState = DoorState.Initialize
