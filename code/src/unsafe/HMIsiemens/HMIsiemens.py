import os
import sys
import time
import loguru
from rich import print
from strings import Figures
from snap7.snap7types import * # type: ignore
import snap7.client as c
import ctypes as ct

class Client:

    # Logger
    _log: None

    # Dettagli per il client S7Comm
    _client: c.Client
    _ip: str = os.getenv("PLCSIEMENS_ADDRESS")
    _port: int = int(os.getenv("PLCSIEMENS_PORT"))
    _rack: int = int(os.getenv("PLCSIEMENS_RACK"))
    _slot: int = int(os.getenv("PLCSIEMENS_SLOT"))

    def __init__(self) -> None: 
        
        #Connessione con il PLC
        self._client = c.Client()
        self._client.connect(self._ip, self._rack, self._slot, self._port)

        # Configurazione del logger
        self._log = loguru.logger

        if self._client.get_connected():
            self._log.debug("Connessione stabilita con il PLC simulato.\n")
        else:
            self._log.debug("Errore nella connessione al PLC simulato.")
            sys.exit(1)

    def close_connection(self) -> None:

        # Disconnessione dal PLC
        self._client.disconnect()
        self._log.warning("PLC disconnesso...")

    def get_error_zone(self, PE:list) -> str:

        if PE[2]:
            return Figures.PROC
        elif PE[5]:
            return Figures.QA
        else:
            return Figures.SC
        
    def resolve_error(self, PE:list) -> None:

        if PE[2]:
            self.write_bit_MK(1, True)
        elif PE[5]:
            self.write_bit_MK(3, True)
        else:
            self.write_bit_MK(6, True)

    def write_bit_PA(self, bit_index:int, value:bool) -> None:

        # self._log.debug("Scrittura dell'area PA")

        # Scrittura: Setto il bit specificato al valore specificato
        pa_data = (ct.c_uint8 * 8)()
        pa_data[bit_index] = value
        self._client.write_area(areas.PA, 0, 0, pa_data) # type: ignore

        # self._log.debug(f"Scritto il bit PA{bit_index} al valore {value}")

    def read_PA(self) -> None:

        # self._log.debug("Lettura dell'area PA")

        # Lettura: Leggo tutta l'area PA
        read_pa = self._client.read_area(areas.PA, 0, 0, 8) # type: ignore
        self._log.debug(f"Area PA: {list(read_pa)}")

    def write_bit_PE(self, bit_index:int, value:bool) -> None:

        # self._log.debug("Scrittura dell'area PE")

        # Scrittura: Setto il bit specificato al valore specificato
        pe_data = (ct.c_uint8 * 8)()
        pe_data[bit_index] = value
        self._client.write_area(areas.PE, 0, 0, pe_data) # type: ignore

        # self._log.debug(f"Scritto il bit PE{bit_index} al valore {value}")

    def read_PE(self) -> list:

        # self._log.debug("Lettura dell'area PE")

        # Lettura: Leggo tutta l'area PE
        read_pe = self._client.read_area(areas.PE, 0, 0, 8) # type: ignore
        # self._log.debug(f"Area PE: {list(read_pe)}")
        return list(read_pe)

    def write_bit_MK(self, bit_index:int, value:bool) -> None:

        # self._log.debug("Scrittura dell'area MK")

        # Scrittura: Setto il bit specificato al valore specificato
        mk_data = (ct.c_uint8 * 8)()
        mk_data[bit_index] = value
        self._client.write_area(areas.MK, 0, 0, mk_data) # type: ignore

        # self._log.debug(f"Scritto il bit MK{bit_index} al valore {value}")

    def read_MK(self) -> list:

        # self._log.debug("Lettura dell'area MK")

        # Lettura: Leggo tutta l'area MK
        read_mk = self._client.read_area(areas.MK, 0, 0, 8) # type: ignore
        # self._log.debug(f"Area MK: {list(read_mk)}")
        return list(read_mk)

    def write_bit_DB(self, bit_index:int, value:bool) -> None:

        # self._log.debug("Scrittura dell'area DB")

        # Scrittura: Setto il bit specificato al valore specificato
        db_data = (ct.c_uint8 * 8)()
        db_data[bit_index] = value
        self._client.write_area(areas.DB, 0, 0, db_data) # type: ignore

        # self._log.debug(f"Scritto il bit DB{bit_index} al valore {value}")

    def read_DB(self) -> None:

        # self._log.debug("Lettura dell'area DB")

        # Lettura: Leggo tutta l'area DB
        read_db = self._client.read_area(areas.DB, 0, 0, 4) # type: ignore
        self._log.debug(f"Area DB0 (tot_product): {int.from_bytes(read_db, byteorder = 'big', signed = False)}")
        read_db = self._client.read_area(areas.DB, 1, 0, 4) # type: ignore
        self._log.debug(f"Area DB1 (tot_defected): {int.from_bytes(read_db, byteorder = 'big', signed = False)}")

    def HMI(self) -> None:
        clear = lambda: os.system("clear")
        while True:
            try:                
                status = cli.read_MK()
                errors = cli.read_PE()

                clear()
                
                if errors[2] or errors[5] or errors[6]:
                    print(Figures.ERRORE + "\n" + cli.get_error_zone(errors))
                    time.sleep(2) # Simuliamo l'intervento dell'operatore
                    print(Figures.RIPRISTINO)
                    cli.resolve_error(errors)
                    time.sleep(1)
                    continue

                if status[4]:
                    print(Figures.OK)
                elif status[5]:
                    print(Figures.X)
                print("\n\n")
                cli.read_DB()
                time.sleep(0.7)

            except KeyboardInterrupt:
                cli.close_connection()
                break

if __name__ == '__main__':

    # Aggiungo il parametro name alle areas (per problemi con la libreria che scarica il container)

    cli = Client()
    cli.HMI()    

