from machine import Pin, UART
import time
import temperature_sensor
import weastatus

uart = UART(1, baudrate=9600, tx=Pin(4), rx=Pin(5))  

prev_time = None
prev_speed = None
esp_signal = Pin(6, Pin.IN)

def calculate_distance(speed2_kmh, time_diff_seconds, current_temp, has_fog, has_snow):
    if time_diff_seconds > 5:
        return "Following distance control unnecessary (time difference > 5s)."

    speed2_mps = speed2_kmh * 1000 / 3600
    following_distance = speed2_mps * time_diff_seconds

    def calc_SD(speed_kmh):
        if esp_signal.value():
            print("Detected: Heavy vehicle")
            fm = 0.2778 * 1.5 * speed_kmh
            sm = (speed_kmh ** 2) / (254 * 0.7)
            return fm + sm
        else:    
            print("Detected: Passenger vehicle")
            v = speed_kmh / 10
            return (v * 3) + (v ** 2 * 0.4)

    is_bad_weather = (
        current_temp is not None and current_temp < 3
    ) or has_fog or has_snow

    if is_bad_weather:
        SD = speed2_kmh  
    else:
        SD = calc_SD(speed2_kmh)

    return {
        "time difference second": time_diff_seconds,
        "following distance meter": round(following_distance, 2),
        "safe stopping meter": round(SD, 2),
        "safe": following_distance >= SD - 5,
        "bad weather": is_bad_weather,
        "current temp": round(current_temp, 2) if current_temp is not None else None,
        "has fog": has_fog,
        "has snow": has_snow
    }

print("Main circuit initialized, waiting for UART data...")

while True:
    if uart.any():
        line = uart.readline()
        try:
            speed = float(line.strip())
            now = time.ticks_ms()

            print(f"\nSpeed data: {speed:.2f} km/h")

            if prev_time is not None:
                time_diff = (time.ticks_diff(now, prev_time)) / 1000

                current_temp = temperature_sensor.read_temperature()

                result = calculate_distance(
                    speed,
                    time_diff,
                    current_temp,
                    weastatus.has_fog,
                    weastatus.has_snow
                )
                print("Result:", result)
                if not result["safe"]:
                    uart.write(b"true")

            prev_time = now
            prev_speed = speed
        except Exception as e:
            print("Error:", e)

    time.sleep(0.1)
