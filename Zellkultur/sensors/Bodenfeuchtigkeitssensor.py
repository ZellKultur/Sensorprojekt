from Zellkultur.sensors.MCP3008 import MCP3008
import time

def setup(channel = 0):
    return {"adc":MCP3008(), "channel":channel}

def read(sensor):
    return sensor["adc"].read(channel=sensor["channel"])

if __name__ == '__main__':
    boden = setup()

    for i in range(100):
        print(f"messung {read(boden)}")
        time.sleep(1)
