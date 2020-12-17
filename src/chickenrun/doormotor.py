from gpiozero import Button,Motor
import time
import signal


class RunMotorTimeoutException(Exception):
    pass


class DoorMotor():
    def __init__(self, motorForwardChannel, motorBackwardChannel, forwardLimitSensorChannel, backwardLimitSensorChannel, forwardTimeout, backwardTimeout):
        self._forwardLimitSensor = Button(forwardLimitSensorChannel)
        self._backwardLimitSensor = Button(backwardLimitSensorChannel)
        self.forwardTimeout = forwardTimeout
        self.backwardTimeout = backwardTimeout
        self._motor = Motor(forward=motorForwardChannel, backward=motorBackwardChannel, pwm=True)
        # security: stop motor when limit are pressed
        self._forwardLimitSensor.when_pressed = self.stop
        self._backwardLimitSensor.when_pressed = self.stop


    def __del__(self):
        self._motor.close()
        self._forwardLimitSensor.close()
        self._backwardLimitSensor.close()


    @property
    def forwardLimitSensorState(self):
        return self._forwardLimitSensor.value


    @property
    def backwardLimitSensorState(self):
        return self._backwardLimitSensor.value


    @property
    def is_active(self):
        return self._motor.is_active


    def forward(self):
        timeout = time.time() + self.forwardTimeout
        while not self.forwardLimitSensorState:
            if time.time() > timeout:
                self.stop()
                raise RunMotorTimeoutException()
            self._motor.forward(1)
        self.stop()


    def backward(self):
        timeout = time.time() + self.backwardTimeout
        while not self.backwardLimitSensorState:
            if time.time() > timeout:
                self.stop()
                raise RunMotorTimeoutException()
            self._motor.backward(1)
        self.stop()


    def stop(self):
        print("Stop !")
        self._motor.stop()

## Test
# test = DoorMotor(motorForwardChannel=19, motorBackwardChannel=26, forwardLimitSensorChannel=17, backwardLimitSensorChannel=23, forwardTimeout=4, backwardTimeout=4)
# print("Motor is active: " + str(test.is_active))
# test.backward()
# print("Motor is active: " + str(test.is_active))
# time.sleep(2)
# test.stop()
# print("Motor is active: " + str(test.is_active))
# time.sleep(0.1)
# test.forward()
# print("Motor is active: " + str(test.is_active))
# time.sleep(2)
# test.stop()
# print("Motor is active: " + str(test.is_active))
