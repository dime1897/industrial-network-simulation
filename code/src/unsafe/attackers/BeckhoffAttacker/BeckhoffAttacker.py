import os
import time
import random as rnd
from pyModbusTCP.client import ModbusClient

def connect_real() -> ModbusClient:
    return ModbusClient(host = os.getenv("PLCBECKHOFF_ADDRESS"), port = int(os.getenv("PLCBECKHOFF_PORT")), auto_open=True)

client = connect_real()
while True:
    start_address = rnd.randint(0,20)
    value = rnd.randint(0,1)    
    client.write_single_coil(start_address, value)
    time.sleep(0.4)