from fins.client import FinsClient

client = FinsClient(host="172.20.3.1", port=9600)
client.connect()

dato = 12456
client.memory_area_write('D1850', dato.to_bytes(2, 'big'), 1)

for i in range(100):
    addr = 'D' + str(1800+i)
    response = client.memory_area_read(addr, 1)
    print(int.from_bytes(response.data, 'big'))

client.close()