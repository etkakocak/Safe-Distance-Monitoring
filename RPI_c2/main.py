from machine import Pin, time_pulse_us, UART
import time

TRIG_PIN = 27
ECHO_PIN = 16
trig = Pin(TRIG_PIN, Pin.OUT)
echo = Pin(ECHO_PIN, Pin.IN)
uart = UART(1, baudrate=9600, tx=Pin(4), rx=Pin(5))
camera_led = Pin(12, Pin.OUT)

violation_triggered = False

def detected_violation():
    camera_led.on()        
    sleep(0.5)        
    camera_led.off()            

# Function to measure distance
def measure_distance():
    trig.low()
    time.sleep_us(2)
    trig.high()
    time.sleep_us(10)
    trig.low()
    
    duration = time_pulse_us(echo, 1)
    
    # Calculate the distance in cm
    distance = (duration / 2) / 29.1
    return distance

# Check if the distance sensor is operating
def check_distance_sensor(distance):
    if distance < 0:
        return False # Distance sensor not working
    else:
        return True

threshold=150
# Radar start
print("Radar initialized. Waiting for vehicle....")
while True:
    distance = measure_distance()
    # print("Distance: ", distance, "cm")
    while distance < threshold and check_distance_sensor(distance):
        start_distance = distance
        start_time = time.ticks_ms()
        while True:
            end_distance = measure_distance()
            # print("End Distance: ", end_distance, "cm")
            if end_distance < 5: 
                end_time = time.ticks_ms()
                break
            time.sleep(0.005)
        delta_d = start_distance - end_distance  # cm
        delta_t = time.ticks_diff(end_time, start_time) / 1000  # sec
        if delta_t > 0:
            speed = delta_d / delta_t  # cm/s actually
            print("Speed:", round(speed, 2), "km/h")
            uart.write(f"{speed:.2f}\n")
            time.sleep(0.005)
            break 
        else:
            print("Calculation error.")
            break

    # print("Waiting for a new vehicle...")
    if uart.any():
        msg = uart.readline()
        if msg and msg.strip() == b"true" and not violation_triggered:
            print("Violation detected!")
            detected_violation()
            violation_triggered = True 

    time.sleep(0.01)
