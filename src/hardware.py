from gpiozero import Button, DistanceSensor
import time

class SmartGlassesHW:
    def __init__(self, button_pin=26, trigger_pin=23, echo_pin=24):
        # 1. Button on GPIO 26
        # pull_up=True means it uses the Pi's internal resistor 
        # (Connect button between GPIO 26 and a Ground pin)
        self.button = Button(button_pin, pull_up=True)
        
        # 2. Ultrasonic Sensor (HC-SR04)
        # Trigger: GPIO 23, Echo: GPIO 24
        self.distance_sensor = DistanceSensor(echo=echo_pin, trigger=trigger_pin)

    def get_distance(self):
        """Returns distance in centimeters."""
        # gpiozero returns distance in meters, we convert to cm
        return round(self.distance_sensor.distance * 100, 2)

    def set_button_callback(self, callback_func):
        """
        Links a function to the button press.
        This runs in the background (using interrupts).
        """
        self.button.when_pressed = callback_func

    def cleanup(self):
        # gpiozero handles cleanup automatically, 
        # but we keep this method for structural consistency.
        pass