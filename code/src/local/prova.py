import fins.tcp
import time

fins_instance = fins.tcp.TCPFinsConnection()
fins_instance.connect('192.168.172.151')
fins_instance.dest_node_add=1
fins_instance.srce_node_add=25

for i in range(2):
    fins_instance.memory_area_write(fins.FinsPLCMemoryAreas().CIO_WORD,b'\x00\x64\x00',b'\x00\x1f',1)
    mem_area = fins_instance.memory_area_read(fins.FinsPLCMemoryAreas().CIO_WORD,b'\x00\x64\x00')
    print(mem_area)
    time.sleep(1)
    fins_instance.memory_area_write(fins.FinsPLCMemoryAreas().CIO_WORD,b'\x00\x64\x00',b'\x00\x00',1)
    mem_area = fins_instance.memory_area_read(fins.FinsPLCMemoryAreas().CIO_WORD,b'\x00\x64\x00')
    print(mem_area)
    time.sleep(1)