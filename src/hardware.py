import RPi.GPIO as GPIO
import time

# --- PIN CONFIGURATION ---
TRIG_PIN = 23
ECHO_PIN = 24
BUTTON_PIN = 26
MIN_DISTANCE_CM = 100 

def setup_gpio():
    """Initializes the physical pins on the Raspberry Pi."""
    GPIO.setmode(GPIO.BCM)
    
    # Ultrasonic Sensor Pins
    GPIO.setup(TRIG_PIN, GPIO.OUT)
    GPIO.setup(ECHO_PIN, GPIO.IN)
    
    # Tactile Button Pin (Uses internal pull-up resistor to prevent static misfires)
    GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    print("⚙️ Hardware GPIO initialized.")

def get_distance():
    """Sends a 10-microsecond ultrasonic pulse and returns the distance in cm."""
    GPIO.output(TRIG_PIN, True)
    time.sleep(0.00001) 
    GPIO.output(TRIG_PIN, False)

    pulse_start, pulse_end = time.time(), time.time()
    timeout = time.time() + 0.1 
    
    # Record the time the soundwave leaves
    while GPIO.input(ECHO_PIN) == 0 and time.time() < timeout:
        pulse_start = time.time()
        
    # Record the time the soundwave bounces back
    while GPIO.input(ECHO_PIN) == 1 and time.time() < timeout:
        pulse_end = time.time()

    # Calculate distance using the speed of sound (17150 cm/s)
    distance = (pulse_end - pulse_start) * 17150
    return round(distance, 2)

def cleanup():
    """Safely releases the hardware pins to prevent crashes on the next boot."""
    GPIO.cleanup()
    print("🔌 Hardware pins safely released.")