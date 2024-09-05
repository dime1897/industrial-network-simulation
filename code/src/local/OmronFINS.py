import time
import socket

class ConnectionStruct:
    _socket: socket.socket
    _ip: str = "192.168.172.151"
    _port: int = 9600
    _buffer: bytearray
    _clientNode: bytes
    _serverNode: bytes

    def leggi_dm(self, cnt, start):
        ret = [0] * cnt
        send = bytearray(34)
        self.add_headers(send)
        send[26] = 1
        send[27] = 1
        send[28] = 82
        self.add_start_end_address(start, send, 29)
        send[31] = 0
        self.add_start_end_address(cnt, send, 32)
        self.send(send)

        if not self.check_errori():
            return None

        j = 0
        for i in range(30, len(self._buffer), 2):
            if j < len(ret):
                ret[j] = (self._buffer[i] << 8 & 0xff00) | (self._buffer[i + 1] & 255)
                if ret[j] > 32767:
                    ret[j] -= 65536
                j += 1
        return ret
    
    def add_headers(self, send):
        send[0] = 70
        send[1] = 73
        send[2] = 78
        send[3] = 83
        send[4] = 0
        send[5] = 0
        send[6] = 0
        send[7] = 34
        send[8] = 0
        send[9] = 0
        send[10] = 0
        send[11] = 2
        send[12] = 0
        send[13] = 0
        send[14] = 0
        send[15] = 0
        send[17] = 0
        send[18] = 2
        send[19] = 0
        send[20] = 0
        send[21] = 0
        send[22] = 0
        send[23] = self._clientNode
        send[24] = 0
        send[25] = 100

    def add_start_end_address(self, start, send, startindex):
        hex_str = f"{start:04x}"
        bt1 = hex_str[:2] if len(hex_str) > 2 else "00"
        bt2 = hex_str[-2:]
        send[startindex] = int(bt1, 16)
        send[startindex + 1] = int(bt2, 16)

    def check_errori(self):
        if len(self._buffer) > 0:
            errore = self._buffer[15]
            if errore == 0:
                return True
            elif errore == 1:
                print("The header is not FINS...")
            elif errore == 2:
                print("The data length is too long...")
            # Add more cases here
            return False
        return False

    def send(self, send):
        try:
            if send is None:
                raise IOError()
            self._socket.send(send)
            self._buffer = self._socket.recv(1024)
            return True
        except (IOError, AttributeError) as e:
            print("Connection lost:", e)
            return False


struct = ConnectionStruct()
struct._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
struct._socket.connect(("192.168.172.151", 9600))

struct._buffer = bytearray(20)
struct._buffer[0] = 70
struct._buffer[1] = 73
struct._buffer[2] = 78
struct._buffer[3] = 83
struct._buffer[4] = 0
struct._buffer[5] = 0
struct._buffer[6] = 0
struct._buffer[7] = 12
struct._buffer[8] = 0
struct._buffer[9] = 0
struct._buffer[10] = 0
struct._buffer[11] = 0
struct._buffer[12] = 0
struct._buffer[13] = 0
struct._buffer[14] = 0
struct._buffer[15] = 0
struct._buffer[16] = 0
struct._buffer[17] = 0
struct._buffer[18] = 0
struct._buffer[19] = 0
struct._socket.send(struct._buffer)
ret = bytearray(struct._socket.recv(1024))

if ret[15] == 0x00:
    print(f"ClientNode: {ret[20]}")
    print(f"ServerNode: {ret[23]}")
    struct._clientNode = ret[20]
    struct._serverNode = ret[23]
else:
    print("Impossibile connettersi al PLC")

print(struct.leggi_dm(5, 1600))