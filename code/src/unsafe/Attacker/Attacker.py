import time
import random as rnd
from fins.client import FinsClient

client = FinsClient(host = "192.168.3.1", port = 9600)
client.connect()

BIT_UP = int(1).to_bytes(1, "big")
BIT_DOWN = int(0).to_bytes(1, "big")

while True:
    bit = rnd.randint(0,2)
    client.memory_area_write("W0." + str(bit), BIT_UP, 1)
    time.sleep(0.2)
    client.memory_area_write("W0." + str(bit), BIT_DOWN, 1)