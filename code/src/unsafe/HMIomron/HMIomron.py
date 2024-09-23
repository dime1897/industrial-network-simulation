import os
import time
import re
from typing import Tuple
from fins import SetResetSpec, SetResetSpecCode, MemoryArea
from fins.client import FinsClient


# ip = os.getenv("PLCOMRON_ADDRESS")
# port = int(os.getenv("PLCOMRON_PORT"))
BIT_UP = 1
BIT_DOWN = 0
ip = "192.168.3.1"
port = 9600

client = FinsClient(host=ip, port=port)
client.connect()
 
# dato = 12456
# client.memory_area_write('D1850', dato.to_bytes(2, 'big'), 1)

# for i in range(100):
    # addr = 'D' + str(1800+i)
    # response = client.memory_area_read(addr, 1)
    # print(int.from_bytes(response.data, 'big'))



while True:
    try:
        """BIT_UP.to_bytes(2, 'big'), 1"""
        client.memory_area_write("W0.3", BIT_UP.to_bytes(1, 'big'), 1)
        # client.forced_set_reset(SetResetSpec(SetResetSpecCode.FORCE_SET, "W0.00"))
        # time.sleep(1)
        # """BIT_DOWN.to_bytes(2, 'big'), 1"""
        # client.forced_set_reset(SetResetSpec(SetResetSpecCode.FORCE_RESET, "CIO0.00"))
        time.sleep(1)
    except KeyboardInterrupt:
        client.forced_set_reset_cancel()
        break

client.close()