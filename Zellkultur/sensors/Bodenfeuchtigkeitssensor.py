import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)


class Bodenfeuchtigkeitssensor:
    def __init__(self, pin):
        GPIO.setup(pin, GPIO.IN)
        self.pin = pin

    def read(self):
        return "HIGH" if GPIO.input(self.pin) == 0 else "LOW"
