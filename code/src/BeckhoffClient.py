import os
import time
import loguru
from Colors import COLORS
from pyModbusTCP.client import ModbusClient

class Client:

    # Logger
    _log: None

    # Dettagli per il client Modbus
    _client: ModbusClient
    _host: str
    _port: int

    def __init__(self, host:str="localhost", port:int=502) -> None:

        # Settaggio parametri per la connessione con il PLC
        self._host = host
        self._port = port

        # Configurazione del logger
        self._log = loguru.logger

        # Connessione con il PLC
        self._client = ModbusClient(host=self._host, port=self._port, auto_open=True)
        
        if not self._client.is_open:
            self._log.error("Impossible connecting to PLC")
        else:
            self._log.debug("Connected to PLC...")

    def read_full_state(self) -> list[bool]:
        
        # Leggiamo lo stato del PLC per aggiornare l'HMI
        return self._client.read_coils(0, 20) # Leggiamo i 10 ingressi e le 10 uscite

    def write_coil(self, start_address:int, value:bool=False) -> None:

        # Scriviamo i False nei bit d'errore quando vogliamo ripristinare un errore
        self._client.write_single_coil(start_address, value)

    def HMI(self) -> None:

        # Per pulire stdout
        clear = lambda: os.system("clear")

        while True:
            # Aggiorniamo lo stato dell'HMI
            time.sleep(0.5) # Ogni mezzo secondo
            state = self.read_full_state()

            clear()

            print(f"{COLORS.FAIL if state[7] else COLORS.ENDC}: || {COLORS.ENDC}" if state[10] else "  ", end="")
            print(f"{COLORS.FAIL if state[7] else COLORS.ENDC}: {COLORS.ENDC}" if state[1] else "  ", end="")
            print(f"{COLORS.FAIL if state[7] else COLORS.ENDC}: {COLORS.ENDC}" if state[3] else "  ", end="")
            print(f"{COLORS.FAIL if state[7] else COLORS.ENDC}: {COLORS.ENDC}" if state[5] else "  ", end="")
            print(f"{COLORS.FAIL if state[9] else COLORS.ENDC}\t\t\t\t\t\t\t____{COLORS.ENDC}" * state[6])
            print(print(f"        \t\t\t  XX  \t\t\t" * (not state[11] and not state[12] and not state[13] and not state[8])))
            print(f"{COLORS.OKCYAN if not state[12] else COLORS.OKGREEN}      XX  \t\t\t\t\t\t\t{COLORS.ENDC}" * (state[11] and not state[8]))
            print(f"{COLORS.OKCYAN if not state[12] else COLORS.OKGREEN}          \t\t\t\t\t\t\t XX{COLORS.ENDC}" * (state[13] and not state[8]))
            print(print(f"{COLORS.FAIL}        \t\t\t  XX  \t\t\t{COLORS.ENDC}" * state[8]))

            if state[7] or state[8] or state[9]:
                self.error_handling()

    def error_handling(self):

        op = int(input("Press the number corresponding to the error resolved.\n\n" + 
                       "1-Picking area error\n" + 
                       "2-Plier error\n" + 
                       "3-Releasing area error\n" + 
                       "4-No error occurred\n\nDone: "))
        if not op in [1,2,3,4]:
            self._log.warning("Invalid input.")
        elif op == 1:
            self._client.write_single_coil(7, False)
        elif op == 2:
            self._client.write_single_coil(8, False)
        elif op == 3:
            self._client.write_single_coil(9, False)
        else:
            self._log.error("Something went wrong")


if __name__ == "__main__":
    cli = Client(port=10502)
    cli.HMI()
