import network
import urequests
import time
import _thread

SSID = "xx"
PASSWORD = "xx"

# OpenWeatherMap API and coord.
API_KEY = "xx"
LAT = "55.7875962"
LON = "13.1320501"

# condition vars
has_fog = False
has_snow = False

def connect_wifi(SSID, PASSWORD):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)
    print("Connecting to WiFi...")
    while not wlan.isconnected():
        time.sleep(1)
    print("Connected to WiFi. IP Address:", wlan.ifconfig()[0])
    return True

class WeatherChecker:
    def __init__(self, api_key, lat, lon):
        self.api_key = api_key
        self.lat = lat
        self.lon = lon
        self.update_weather()

    def update_weather(self):
        global has_fog, has_snow
        try:
            url = f"http://api.openweathermap.org/data/2.5/weather?lat={self.lat}&lon={self.lon}&appid={self.api_key}"
            response = urequests.get(url)
            data = response.json()
            response.close()

            weather_conditions = [w["main"].lower() for w in data.get("weather", [])]
            print("Weather:", weather_conditions)

            has_fog = "fog" in weather_conditions
            has_snow = "snow" in weather_conditions
        except Exception as e:
            print("API error:", e)
            has_fog = False
            has_snow = False

def weather_updater():
    if connect_wifi(SSID, PASSWORD):
        checker = WeatherChecker(API_KEY, LAT, LON)
        while True:
            checker.update_weather()
            time.sleep(300)  # 5 min
    else:
        print("Wi-Fi error.")

_thread.start_new_thread(weather_updater, ())

