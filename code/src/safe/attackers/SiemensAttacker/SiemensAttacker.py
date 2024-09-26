import os
import time
import random as rnd
from fins.client import FinsClient

def connect_real() -> FinsClient:
    client = FinsClient(host = os.getenv("PLCOMRON_REAL_ADDRESS"), port = int(os.getenv("PLCOMRON_PORT")))
    client.connect()
    return client

def connect_fake() -> FinsClient:
    client = FinsClient(host = os.getenv("PLCOMRON_FAKE_ADDRESS"), port = int(os.getenv("PLCOMRON_PORT")))
    client.connect()
    return client
    
    
BIT_UP = int(1).to_bytes(1, "big")
BIT_DOWN = int(0).to_bytes(1, "big")

while True:
    bit = rnd.randint(0,2)
    client = connect_real()
    try:
        client.memory_area_write("W0." + str(bit), BIT_UP, 1)
    except Exception as e:
        print(str(e))
        client = connect_fake()
        client.memory_area_write("W0." + str(bit), BIT_UP, 1)

    time.sleep(0.2)
    client.memory_area_write("W0." + str(bit), BIT_DOWN, 1)