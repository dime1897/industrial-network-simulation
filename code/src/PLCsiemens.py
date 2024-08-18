import threading
import snap7 as snp
import ctypes as ct
import loguru
from snap7.types import *
from snap7.util import *

"""
Definiamo una classe Siemens che sostanzialmente sarà 
il nostro PLC Siemens che comunica mediante protocollo 
S7Comm (implementato dalla libreria snap7 per noi).
"""

class Siemens:

    # Logger
    _log: None

    # Dettagli del PLC
    _server: snp.server.Server
    _memory_area_size: int
    _data_block_number: int
    _PA: ctypes.Array
    _PE: ctypes.Array
    _MK: ctypes.Array
    _DB: list

    # Failure rate
    _processing_failure_rate: float
    _quality_assurance_failure_rate: float

    def __init__(self):

        # Settaggio della dimensione (in byte) delle aree di memoria
        self._memory_area_size = 8
        self._data_block_number = 5

        # Creazione del server
        self._server = snp.server.Server()

        # Creazione dei buffer per le aree di memoria        
        self._PA = (ctypes.c_uint8 * self._memory_area_size)()  # Output Process Area (PA)
        self._PE = (ctypes.c_uint8 * self._memory_area_size)()  # Input Process Area (PE)
        self._MK = (ctypes.c_uint8 * self._memory_area_size)()  # Merker Memory (MK)
        self._DB = [None] * self._data_block_number  # Data Block Area (DB)

        # Registrazione delle aree di memoria nel nostro server
        self._server.register_area(srvAreaPA, 0, self._PA)  # Uscite fisiche
        self._server.register_area(srvAreaPE, 0, self._PE)  # Ingressi fisici
        self._server.register_area(srvAreaMK, 0, self._MK)  # Merker Memory
        for i in range(self._data_block_number):
            self._DB[i] = (ctypes.c_uint8 * self._memory_area_size)()
            self._server.register_area(srvAreaDB, i, self._DB[i])  # Data Blocks


        # Configurazione del logger
        self._log = loguru.logger

        self._log.debug("Server configuration ended...")

    def processing_routine(self):
        time.sleep(10) # Per simulare la lavorazione
        self._PE[0] = False
        self._MK[1] = False
        
        self._server.unregister_area(srvAreaPE, 0)
        self._server.register_area(srvAreaPE, 0, self._PE)

        self._server.unregister_area(srvAreaMK, 1)
        self._server.register_area(srvAreaMK, 1, self._MK)

    def run(self):

        self._server.start(22000)
        self._log.debug("Server started...")

        try:
            while True:
                event = self._server.pick_event() # Serve solo per loggare gli eventi, non è necessario al funzionamento del server
                if event:
                    self._log.info(f"Event found: {self._server.event_text(event)}")
                
                # Implementazione della logica di controllo
                """
                L'idea della logica di controllo è molto semplice:
                supponiamo di avere un macchinario A (a monte) che deve lavorare un pezzo, quindi il flusso di lavoro sarà:
                    - caricamento del pezzo sul piano di lavoro;
                    - lavorazione del pezzo;
                    - verifica (controllo qualità);
                    - scarico del pezzo (con trigger al PLC a valle).
                Dunque faremo uso di:
                    - PE0.0 --> trigger al PLC che il pezzo è stato caricato sul piano di lavoro
                    - PA0.0 --> il PLC triggera l'attutore che avvia la lavorazione del pezzo (non dettaglieremo la lavorazione per semplicità)
                    - MK1.0 --> lavorazione in corso
                    - PE1.0 --> trigger al PLC che la lavorazione è terminata con successo
                    - PE1.1 --> trigger al PLC che durante la lavorazione si sono riscontrati problemi
                    - PA1.0 --> il PLC triggera l'attuatore che avvia il processo di controllo qualità (non dettagliato per lo stesso motivo)
                    - PA1.1 --> il PLC triggera la sirena della zona di lavorazione
                    - MK2.0 --> controllo qualità in corso
                    - PE2.0 --> trigger al PLC che il pezzo è conforme
                    - PE2.1 --> trigger al PLC che il pezzo è da scartare
                    - PE2.2 --> trigger al PLC che durante il controllo qualità del pezzo si sono riscontrati problemi
                    - MK3.0 --> chiusura flusso di lavoro in corso
                    - PA3.0 --> il PLC triggera l'attuatore che scaricherà il pezzo e comunicherà alla macchina a valle che il pezzo è pronto
                    - PA3.1 --> il PLC triggera l'attuatore che scarterà il pezzo
                    - PA3.2 --> il PLC triggera la sirena della zona di controllo qualità
                """
                if self._PE[0] and not self._MK[1]:
                    # Il pezzo è stato caricato sul piano di lavoro e la lavorazione non è in corso
                    self._log.debug("Starting processing routine...")
                    self._MK[1] = True
                    threading.Thread(target=self.processing_routine).start()

                if self._MK[1]:
                    self._log.debug("Processing.....")


                # Attesa di 1 secondo prima del prossimo ciclo
                time.sleep(1)
        except KeyboardInterrupt:
            self._log.warning("Server manually blocked...")
        finally:
            self._server.stop()
            self._log.warning("Destroying server...")
            self._server.destroy()

if __name__ == '__main__':

    PLC = Siemens()
    PLC.run()
