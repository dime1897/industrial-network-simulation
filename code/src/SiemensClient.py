import snap7

PLC = snap7.client.Client()

PLC.connect("127.0.0.1", 0, 0, 102)
print(PLC.get_connected())
data = PLC.db_read(2,0,8)
print(data)
hw = b"Hello World gyus!"
PLC.db_write(2,0,hw)

data = PLC.db_read(2,0,16)
print(data.decode('ascii'))