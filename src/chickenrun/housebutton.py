from gpiozero import Button
import time
import signal


class PressButton():
    def __init__(self, buttonGpioPin, onPressedCallback, onHeldCallback, holdTime=10):
        self.buttonGpioPin = buttonGpioPin
        self.onPressedCallback = onPressedCallback
        self.onHeldCallback = onHeldCallback
        self._button = Button(buttonGpioPin)
        self._button.hold_time = holdTime
        self._button.when_pressed = self.onPressedCallback
        self._button.when_held = self.onHeldCallback
