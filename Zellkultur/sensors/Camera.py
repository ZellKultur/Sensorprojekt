from picamera import PiCamera
import time
import datetime
import os


def create_testbilder_path(path):
    if not os.path.isdir(path):
        os.makedirs(path)


def take_picture(filepath):
    camera = PiCamera()
    camera.start_preview()
    time.sleep(2) # Camera needs to "preheat" to focus
    camera.capture(filepath)
    camera.stop_preview()


def timestampname():
    timestamp = datetime.datetime.now().isoformat()
    timestamp_without_colon = "".join([c if not c == ":" else "_" for c in timestamp])
    return f'image{timestamp_without_colon}.jpg'

