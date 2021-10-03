import datetime
import threading
import time
import config
import sensors.Temp_HumiditySensor
import sensors.Bodenfeuchtigkeitssensor
import sensors.Camera
import sensors.LED
import os
import RPi.GPIO

def setup_csv(): #kommentar
    if not os.path.isfile(config.CSV_FILENAME):
        with open(config.CSV_FILENAME, "w+") as file:
            file.write("Timestamp; Temperatur; Luftfeuchtigkeit; Bodenfeuchtigkeit;\n")


def read_tempsensor(temp_sensor, shared_data):
    for i in range(config.SENSOR_MAXTRIES):
        try:
            temp_data = sensors.Temp_HumiditySensor.read(temp_sensor)
            shared_data["tempsensor"] = temp_data
            return
        except ValueError:
            time.sleep(config.SENSOR_SLEEP_BETWEEN_TRIES_SECONDS)
    shared_data["tempsensor"] = {"temp": -1, "humidity": -1, "timestamp": datetime.datetime.now()}
    return


def read_bodensensor(boden_sensor, shared_data):
    data = boden_sensor.read()
    shared_data["bodensensor"] = data
    if data == "LOW":
        sensors.LED.on(config.NEEDS_WATER_LED_PIN)
    else:
        sensors.LED.off(config.NEEDS_WATER_LED_PIN)

    return


def read_camera(skip):
    if skip:
        return
    print("say cheese!")
    sensors.Camera.create_testbilder_path(config.IMAGE_PATH)
    filename = sensors.Camera.timestampname()
    filepath = f"{config.IMAGE_PATH}/{filename}"
    sensors.Camera.take_picture(filepath)
    print("took a picture")
    return


def write_data_to_csv(data_to_write):
    tempdata = data_to_write["tempsensor"]
    bodendata = data_to_write["bodensensor"]
    with open(config.CSV_FILENAME, "a") as file:
        timestamp = tempdata["timestamp"].strftime('%Y-%m-%d %H:%M:%S')
        temperatur = tempdata["temp"]
        humidity = tempdata["humidity"]
        bodenfeuchtigkeit = bodendata
        line = f"{timestamp}, {temperatur}, {humidity}, {bodenfeuchtigkeit},\n"
        file.write(line)


def write_data_to_cli(data_to_write):
                timestamp = data_to_write["tempsensor"]["timestamp"].strftime('%Y-%m-%d %H:%M:%S')
                bodendata = data_to_write["bodensensor"]
                temperatur = data_to_write["tempsensor"]["temp"]
                feuchtigkeit = data_to_write["tempsensor"]["humidity"]
                print(f"{timestamp} Bodenfeuchtigkeit: {bodendata:>4} Temperatur: {temperatur:>6.2f}°C Luftfeuchtigkeit: {feuchtigkeit:>6.2f}%")


def sleep_till_next_tick(anchor_time, tick_interval):
    """This function sleeps till the next sheduled tick interval comes around.
    This important as sleep(60) might wait a fraction of a second more then 60. Thus over many minutes,
    the intervals will get out of synch.
    This function resynches automatically.

    :param anchor_time:
    :param tick_interval:
    :return:
    """
    time.sleep(tick_interval - (time.time() - anchor_time) % tick_interval)


if __name__ == '__main__':
    tempsensor = sensors.Temp_HumiditySensor.setup(config.TEMPSENSORPIN)
    bodensensor = sensors.Bodenfeuchtigkeitssensor.Bodenfeuchtigkeitssensor(config.BODENSENSORPIN)
    setup_csv()
    starting_time = time.time()
    camera_skip_counter = 0
    try:
        sensors.LED.setup(config.ALWAYS_ON_LED_PIN)
        sensors.LED.setup(config.NEEDS_WATER_LED_PIN)
        sensors.LED.on(config.ALWAYS_ON_LED_PIN)
        while True:
            shared_thread_data = {}

            temp_thread = threading.Thread(target=read_tempsensor, args=(tempsensor, shared_thread_data))
            boden_thread = threading.Thread(target=read_bodensensor, args=(bodensensor, shared_thread_data))
            camera_thread = threading.Thread(target=read_camera, args=(camera_skip_counter != 0,))


            temp_thread.start()
            boden_thread.start()
            camera_thread.start()

            temp_thread.join()
            boden_thread.join()
            camera_thread.join()

            write_data_to_csv(shared_thread_data)
            write_data_to_cli(shared_thread_data)

            camera_skip_counter += 1
            camera_skip_counter %= config.CAMERA_SKIP_MEASUREMENTS
            sleep_till_next_tick(starting_time, config.MAIN_LOOP_TICK_SECONDS)
    finally:
        RPi.GPIO.cleanup()
