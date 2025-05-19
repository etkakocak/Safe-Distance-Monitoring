import machine
import onewire
import ds18x20
import time

# DS18B20 sensor onewire connect
ds_pin = machine.Pin(28)
ow = onewire.OneWire(ds_pin)
ds = ds18x20.DS18X20(ow)

roms = ds.scan() # sensor roms
if not roms:
    print("No sensor found.")
else:
    print(f"{len(roms)} DS18B20 found.")

# temp var
current_temp = None

def read_temperature():
    global current_temp
    if not roms:
        current_temp = None
        return
    ds.convert_temp()
    time.sleep_ms(750)
    for rom in roms:
        temp = ds.read_temp(rom)
        current_temp = temp
        print(f"Updated temperature: {temp:.2f}°C")
    return temp
