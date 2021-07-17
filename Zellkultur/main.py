import datetime
import threading
import time
import config
import sensors.Temp_HumiditySensor
import sensors.Bodenfeuchtigkeitssensor
import sensors.Camera
import os

def setup_csv():
    if not os.path.isfile(config.CSV_FILENAME):
        with open(config.CSV_FILENAME, "w+") as file:
            file.write("Timestamp; temp; humidity; bodenfeuchtigkeit;\n")


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
    shared_data["bodensensor"] = boden_sensor.read()
    return


def write_data_to_csv(data_to_write):
    tempdata = data_to_write["tempsensor"]
    bodendata = data_to_write["bodensensor"]
    with open(config.CSV_FILENAME) as file:
        timestamp = tempdata["timestamp"]
        temperatur = tempdata["temp"]
        humidity = tempdata["humidity"]
        bodenfeuchtigkeit = bodendata
        line = f"{timestamp}, {temperatur}, {humidity}, {bodenfeuchtigkeit},\n"
        file.write(line)


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
    bodensensor = sensors.Bodenfeuchtigkeitssensor.Bodenfeuchtigkeitssensor(config.BODENSENSORMCPCHANNEL)
    setup_csv()
    starting_time = time.time()

    while True:
        shared_thread_data = {}

        temp_thread = threading.Thread(target=read_tempsensor, args=(tempsensor, shared_thread_data))
        boden_thread = threading.Thread(target=read_bodensensor, args=(bodensensor, shared_thread_data))

        temp_thread.start()
        boden_thread.start()

        temp_thread.join()
        boden_thread.join()

        sleep_till_next_tick(starting_time, config.MAIN_LOOP_TICK_SECONDS)
