import loguru
import snap7.client as c
from snap7.util import *
from snap7.types import *

class Client:

    # Logger
    _log: None

    # Dettagli per il client S7Comm
    _client: c.Client
    _ip: str
    _port: int
    _rack: int
    _slot: int

    def __init__(self, ip:str="127.0.0.1", rack:int=0, slot:int=1, port:int=10102) -> None: #102 È la porta di S7Comm, ho messo la 10102 solo per non dover fare sudo tutte le volte

        # Settaggio parametri per connessione al PLC
        self._ip = ip
        self._rack = rack
        self._slot = slot
        self._port = port

        #Connessione con il PLC
        self._client = c.Client()
        self._client.connect(self._ip, self._rack, self._slot, self._port)

        # Configurazione del logger
        self._log = loguru.logger

        if self._client.get_connected():
            self._log.debug("Connessione stabilita con il PLC simulato.\n")
        else:
            self._log.debug("Errore nella connessione al PLC simulato.")

    def close_connection(self) -> None:

        # Disconnessione dal PLC
        self._client.disconnect()
        self._log.warning("PLC disconnesso...")

    def write_bit_PA(self, bit_index:int, value:bool) -> None:

        self._log.debug("Scrittura dell'area PA")

        # Scrittura: Setto il bit specificato al valore specificato
        pa_data = (ctypes.c_uint8 * 8)()
        pa_data[bit_index] = value
        self._client.write_area(Areas.PA, 0, 0, pa_data)

        self._log.debug(f"Scritto il bit PA{bit_index} al valore {value}")

    def read_PA(self) -> None:

        self._log.debug("Lettura dell'area PA")

        # Lettura: Leggo tutta l'area PA
        read_pa = self._client.read_area(Areas.PA, 0, 0, 8)
        self._log.debug(f"Area PA: {list(read_pa)}")

    def write_bit_PE(self, bit_index:int, value:bool) -> None:

        self._log.debug("Scrittura dell'area PE")

        # Scrittura: Setto il bit specificato al valore specificato
        pe_data = (ctypes.c_uint8 * 8)()
        pe_data[bit_index] = value
        self._client.write_area(Areas.PE, 0, 0, pe_data)

        self._log.debug(f"Scritto il bit PE{bit_index} al valore {value}")

    def read_PE(self) -> None:

        self._log.debug("Lettura dell'area PE")

        # Lettura: Leggo tutta l'area PE
        read_pe = self._client.read_area(Areas.PE, 0, 0, 8)
        self._log.debug(f"Area PE: {list(read_pe)}")

    def write_bit_MK(self, bit_index:int, value:bool) -> None:

        self._log.debug("Scrittura dell'area MK")

        # Scrittura: Setto il bit specificato al valore specificato
        mk_data = (ctypes.c_uint8 * 8)()
        mk_data[bit_index] = value
        self._client.write_area(Areas.MK, 0, 0, mk_data)

        self._log.debug(f"Scritto il bit MK{bit_index} al valore {value}")

    def read_MK(self) -> None:

        self._log.debug("Lettura dell'area MK")

        # Lettura: Leggo tutta l'area MK
        read_mk = self._client.read_area(Areas.MK, 0, 0, 8)
        self._log.debug(f"Area MK: {list(read_mk)}")

    def write_bit_DB(self, bit_index:int, value:bool) -> None:

        self._log.debug("Scrittura dell'area DB")

        # Scrittura: Setto il bit specificato al valore specificato
        db_data = (ctypes.c_uint8 * 8)()
        db_data[bit_index] = value
        self._client.write_area(Areas.DB, 0, 0, db_data)

        self._log.debug(f"Scritto il bit DB{bit_index} al valore {value}")

    def read_DB(self) -> None:

        self._log.debug("Lettura dell'area DB")

        # Lettura: Leggo tutta l'area DB
        read_db = self._client.write_area(Areas.DB, 0, 0, 4)
        self._log.debug(f"Area DB0 (tot_product): {int.from_bytes(read_db, byteorder = 'big', signed = False)}")
        read_db = self._client.write_area(Areas.DB, 1, 0, 4)
        self._log.debug(f"Area DB1 (tot_defected): {int.from_bytes(read_db, byteorder = 'big', signed = False)}")

    def HMI(self) -> None:
        while True:
            try:
                op = int(input("Cosa desideri fare?\n\n" + 
                               "1-Ricomincia il flusso\n" + 
                               "2-Gestisci errore in lavorazione\n" + 
                               "3-Gestisci errore in controllo qualità\n" + 
                               "4-Gestisci errore in scarico/scarto\n" + 
                               "5-Leggi aree di memoria\n" + 
                               "6-Stop\n\n"))
                if not op in [1,2,3,4,5,6]:
                    print("Operazione non valida.")
                elif op == 1:
                    # Avvio della logica di controllo
                    cli.write_bit_PE(0,True)
                elif op == 2:
                    #Gestione dell'errore (PROC)
                    cli.write_bit_MK(1,True)
                elif op == 3:
                    #Gestione dell'errore (QA)
                    cli.write_bit_MK(3,True)
                elif op == 4:
                    #Gestione dell'errore (SCA)
                    cli.write_bit_MK(6,True)
                elif op == 5:
                    cli.read_PE()
                    cli.read_PA()
                    cli.read_MK()
                    cli.read_DB()
                else:
                    cli.close_connection()
                    break
            except ValueError:
                print("Inserisci un numero tra quelli proposti!!")

if __name__ == '__main__':

    cli = Client()
    cli.HMI()    

