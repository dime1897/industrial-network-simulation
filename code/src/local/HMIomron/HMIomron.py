import os
import time
from fins.client import FinsClient

ip = os.getenv("PLCOMRON_ADDRESS")
port = int(os.getenv("PLCOMRON_PORT"))

client = FinsClient(host=ip, port=port)
client.connect()

dato = 12456
client.memory_area_write('D1850', dato.to_bytes(2, 'big'), 1)

for i in range(100):
    addr = 'D' + str(1800+i)
    response = client.memory_area_read(addr, 1)
    print(int.from_bytes(response.data, 'big'))

while True:
    try:
        time.sleep(1)
    except KeyboardInterrupt:
        break

client.close()