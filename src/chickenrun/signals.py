from gpiozero import LED, PWMLED
import time
from enum import Enum


class InvalidSignalState(Exception):
    pass

class SignalState(Enum):
    Initialize = 0
    UpAndRuning = 1
    DoorTimeoutError = 2
    NetworkOK = 3
    NetworkError = 4
    DoorOperating = 5



class Signal():
    def __init__(self, ledRedGpioPin, ledGreenGpioPin, ledBlueGpioPin, buzzerGpioPin, initalState=SignalState.Initialize):
        self._red = PWMLED(ledRedGpioPin)
        self._green = PWMLED(ledGreenGpioPin)
        self._blue = PWMLED(ledBlueGpioPin)
        self._buzzer = LED(buzzerGpioPin)
        self._state = None
        self.state = initalState

    def __del__(self):
        self._red.close()
        self._green.close()
        self._blue.close()
        self._buzzer.close()

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        if isinstance(value, SignalState):
            self.__applyState(value)
            self._state = value
        else:
            raise InvalidSignalState()
        return self._state


    def networkError(self):
        self.state = SignalState.NetworkError


    def networkOK(self):
        self.state = SignalState.NetworkOK


    def __applyState(self, state):
        if state != self._state:
            if state == SignalState.Initialize:
                # Initialize signal:
                # 1 medium buzzer
                # blue and green fast blinking
                self.__reset()
                self._buzzer.blink(n=1, on_time=2)
                self._green.blink(on_time=0.2, off_time=0.1, fade_in_time=0.1, fade_out_time=0.1)
                self._blue.blink(on_time=0.2, off_time=0.1, fade_in_time=0.1, fade_out_time=0.1)
            elif state == SignalState.UpAndRuning:
                # UpAndRuning signal:
                # blue and green on
                self._red.off()
                self._buzzer.off()
                self._green.on()
            elif state == SignalState.NetworkOK:
                # NetworkOK signal:
                # blue on
                self._buzzer.off()
                self._blue.on()
            elif state == SignalState.DoorTimeoutError:
                # DoorTimeoutError signal:
                # 5 shorts buzzer + 1 short every 20 seconds
                # red blink
                self._red.off()
                self._buzzer.off()
                self._green.on()
                self._buzzer.blink(n=5, on_time=0.5, off_time=0.1)
                self._red.blink(on_time=0.2, off_time=0.1, fade_in_time=0.1, fade_out_time=0.1)
                time.sleep(3)
                self._buzzer.blink(on_time=0.5, off_time=20)
            elif state == SignalState.NetworkError:
                # NetworkError signal:
                # 4 shorts buzzer + 1 short every 20 seconds
                # green blink and blue off
                self._buzzer.off()
                self._blue.off()
                self._buzzer.blink(n=4, on_time=0.5, off_time=0.1)
                self._red.blink(on_time=0.2, off_time=0.1, fade_in_time=0.1, fade_out_time=0.1)
                time.sleep(2.5)
                self._buzzer.blink(on_time=0.5, off_time=20)
            elif state == SignalState.DoorOperating:
                # DoorOperating signal:
                # 1 long buzzer + medium buzzer blink
                # green blink
                self._buzzer.off()
                self._buzzer.blink(n=1, on_time=2, off_time=0.1)
                self._green.blink(on_time=0.3, off_time=0.1, fade_in_time=0.2, fade_out_time=0.2)
                time.sleep(5)
                self._buzzer.blink(on_time=1, off_time=0.4)



    def __reset(self):
        self._red.off()
        self._green.off()
        self._blue.off()
        self._buzzer.off()
