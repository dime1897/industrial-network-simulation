import random as rnd
class Siemens:

    def __init__(self) -> None:
        self._inp = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self._out = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    def setup(self, filename:str) -> None:
        self._inp[rnd.randint(0,len(self._inp)-1)], self._inp[rnd.randint(0,len(self._inp)-1)], self._inp[rnd.randint(0,len(self._inp)-1)] = 1, 1, 1
        print("Setup done...")

    def routine(self) -> None:
        for i in range(10):
            print(self._inp)
            print("Executing routine...")

    def send(self) -> None:
        print("Sending...")

    def receive(self) -> None:
        print("Receiving...")

if __name__ == '__main__':
    PLC = Siemens()
    PLC.setup(filename="blablabla")
    PLC.routine()
    PLC.send()
    PLC.receive()