import RPi.GPIO as GPIO
import dht11
import time
import datetime

def setup(pin=4):
    GPIO.setmode(GPIO.BCM)
    return dht11.DHT11(pin=pin)

def read(sensor):
    result = sensor.read()
    if result.is_valid():
        return {"temp": result.temperature,
         "humidity": result.humidity,
         "timestamp": datetime.datetime.now()}
    else:
        raise ValueError("can't read")

if __name__ == '__main__':
    try:
        for runtime in range(0,1800):
            dht = setup()
            try:
                data = read(dht)
                timestamp = data["timestamp"].strftime('%Y-%m-%d %H:%M:%S')
                hum = data["humidity"]
                temp = data["temp"]
                print(f"Last valid input: {timestamp}" )

                print(f"Temperature: {temp} C")
                print(f"Humidity: {hum} %")
            except ValueError:
                pass # Just ignore failures to read
            finally:
                time.sleep(1)
    finally:
        GPIO.cleanup() #"saubermachen - liest sonst weiter"
