import os
import time
import random as rnd
from pyModbusTCP.client import ModbusClient

def connect_real() -> ModbusClient:
    return ModbusClient(host = os.getenv("PLCBECKHOFF_REAL_ADDRESS"), port = int(os.getenv("PLCBECKHOFF_PORT")), auto_open=True, timeout=2)

def connect_fake() -> ModbusClient:
    return ModbusClient(host = os.getenv("PLCBECKHOFF_FAKE_ADDRESS"), port = int(os.getenv("PLCBECKHOFF_PORT")), auto_open=True, timeout=2)

while True:
    client = connect_real()
    if not client.is_open:
        print("Connection Refused")
        client = connect_fake()
        if not client.is_open:
            print("Network Unreachable")
    start_address = rnd.randint(0,20)
    value = rnd.randint(0,1)
    client.write_single_coil(start_address, value)
    time.sleep(0.4)