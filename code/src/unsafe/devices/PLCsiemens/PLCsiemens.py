import threading
import loguru
import time
import os
import random as rnd
import snap7 as snp
import ctypes as ct
from fins.client import FinsClient

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
    _memory_area_size: int = int(os.getenv("MEMORY_AREA_SIZE"))
    _data_block_number: int = int(os.getenv("DATA_BLOCK_NUMBER"))
    _PA: ct.Array
    _PE: ct.Array
    _MK: ct.Array
    _DB: list
    _port: int = int(os.getenv("PLCSIEMENS_PORT"))
    _sleep_time: float = float(os.getenv("SLEEP_TIME"))

    # Failure rate
    _processing_failure_rate: float = float(os.getenv("PROCESSING_FAILURE_RATE"))
    _quality_assurance_failure_rate: float = float(os.getenv("QUALITY_ASSURANCE_FAILURE_RATE"))
    _defect_rate: float = float(os.getenv("DEFECT_RATE"))
    _discarding_or_sending_failure_rate: float = float(os.getenv("DISCARDING_OR_SENDING_FAILURE_RATE"))

    # Variabili per il monitoraggio della produzione
    _tot_production: int = 0
    _tot_defected: int = 0

    # Client PLC Omron
    _client_omron: FinsClient
    _plcomron_address: str = os.getenv("PLCOMRON_ADDRESS")
    _plcomron_port: int = int(os.getenv("PLCOMRON_PORT"))
    _bit_up: bytearray = int(1).to_bytes(1, 'big')

    def __init__(self):

        # Creazione del server
        self._server = snp.server.Server()

        # Creazione dei buffer per le aree di memoria        
        self._PA = (ct.c_uint8 * self._memory_area_size)()  # Output Process Area (PA)
        self._PE = (ct.c_uint8 * self._memory_area_size)()  # Input Process Area (PE)
        self._MK = (ct.c_uint8 * self._memory_area_size)()  # Merker Memory (MK)
        self._DB = [None] * self._data_block_number  # Data Block Area (DB)

        # Registrazione delle aree di memoria nel nostro server
        self._server.register_area(1, 0, self._PA)  # Uscite fisiche srvAreaPA
        self._server.register_area(0, 0, self._PE)  # Ingressi fisici srvAreaPE
        self._server.register_area(2, 0, self._MK)  # Merker Memory srvAreaMK
        for i in range(self._data_block_number):
            self._DB[i] = (ct.c_uint8 * 4)() # I Data Block dono da 4 byte l'uno
            self._server.register_area(5, i, self._DB[i])  # Data Blocks srvAreaDB
        
        # Configurazione del logger
        self._log = loguru.logger

        # Connessione al PLC Omron
        self._client_omron = FinsClient(host = self._plcomron_address, port = self._plcomron_port)
        self._client_omron.connect()

        self._log.debug(f"Server configuration ended...")

    def processing_routine(self):
        time.sleep(self._sleep_time) # Per simulare la lavorazione

        # Aggiorniamo gli ingressi fisici
        self._PE[0], self._MK[0] = False, False

        # Simuliamo la possibilità che avvenga un fail durante la lavorazione
        if rnd.random() < self._processing_failure_rate:
            self._PE[2] = True # Per triggerare al PLC che durante la lavorazione si sono riscontrati problemi
        else:
            self._PE[1] = True # Per triggerare al PLC che la lavorazione si è conclusa correttamente
        self._log.debug("Processing ended...")

    def quality_assurance_routine(self):
        
        time.sleep(self._sleep_time) # Per simulare il controllo qualità
        
        # Aggiorniamo gli ingressi fisici
        self._PE[1], self._MK[2] = False, False
        
        # Simuliamo la possibilità che avvenga un fail durante il controllo qualità
        if rnd.random() < self._quality_assurance_failure_rate:
            self._PE[5] = True # Per triggerare al PLC che durante il controllo qualità si sono riscontrati problemi
        elif rnd.random() < self._defect_rate:
            self._PE[4] = True # Per triggerare al PLC che il pezzo è da scartare
        else:
            self._PE[3] = True # Per triggerare al PLC che il pezzo ha superato il controllo qualità
        self._log.debug("Quality assurance process ended...")

    def discard_or_send_product(self, arg:list):
        time.sleep(self._sleep_time) # Per simulare che il pezzo viene scartato

        if "discard" in arg:    
            # Aggiorniamo gli ingressi fisici
            self._PE[4], self._MK[5] = False, False

            # Aggiorniamo il contatore
            self._tot_defected += 1
            bytes = self._tot_defected.to_bytes(4, byteorder = 'big', signed = False)
            for i in range(4):
                self._DB[1][i] = bytes[i]

            if rnd.random() < self._discarding_or_sending_failure_rate:
                self._PE[6] = True
            else:
                self._MK[7] = True
            self._client_omron.memory_area_write("W0.1", self._bit_up, 1)
            self._log.debug("Product discarded...")
            self._PE[0] = True

        elif "send" in arg:
            # Aggiorniamo gli ingressi fisici
            self._PE[3], self._MK[4] = False, False

            # Aggiorniamo il contatore
            self._tot_production += 1
            bytes = self._tot_production.to_bytes(4, byteorder = 'big', signed = False)
            for i in range(4):
                self._DB[0][i] = bytes[i]


            if rnd.random() < self._discarding_or_sending_failure_rate:
                self._PE[6] = True
            else:
                self._MK[7] = True
            self._client_omron.memory_area_write("W0.0", self._bit_up, 1)
            self._log.debug("Product properly sent...")
            self._PE[0] = True

    def run(self):

        self._server.start(self._port)
        self._log.debug("Server started...")

        #Avvio il primo ciclo
        self._PE[0] = True
        try:
            while True:
                # event = self._server.pick_event() # Serve solo per loggare gli eventi, non è necessario al funzionamento del server
                # if event:
                    # self._log.info(f"Event found: {self._server.event_text(event)}")
                
                # Implementazione della logica di controllo
                """
                L'idea della logica di controllo è molto semplice:
                supponiamo di avere un macchinario A (a monte) che deve lavorare un pezzo, quindi il flusso di lavoro sarà:
                    - caricamento del pezzo sul piano di lavoro;
                    - lavorazione del pezzo;
                    - verifica (controllo qualità);
                    - scarico del pezzo (con trigger al PLC a valle).
                Dunque faremo uso di:
                    - PE0 --> trigger al PLC che il pezzo è stato caricato sul piano di lavoro
                    - PA0 --> il PLC triggera l'attutore che avvia la lavorazione del pezzo (non dettaglieremo la lavorazione per semplicità)
                    - MK0 --> lavorazione in corso
                    - PE1 --> trigger al PLC che la lavorazione è terminata con successo
                    - PE2 --> trigger al PLC che durante la lavorazione si sono riscontrati problemi
                    - PA1 --> il PLC triggera l'attuatore che avvia il processo di controllo qualità (non dettagliato per lo stesso motivo)
                    - PA2 --> il PLC triggera la sirena della zona di lavorazione
                    - MK1 --> il PLC viene triggerato dall'utente per comunicare che è stata ripristinata la condizione di failure (PORC)
                    - MK2 --> controllo qualità in corso
                    - PE3 --> trigger al PLC che il pezzo è conforme
                    - PE4 --> trigger al PLC che il pezzo è da scartare
                    - PE5 --> trigger al PLC che durante il controllo qualità del pezzo si sono riscontrati problemi
                    - MK3 --> il PLC viene triggerato dall'utente per comunicare che è stata ripristinare la condizione di failure (QA)
                    - PA3 --> il PLC triggera l'attuatore che scaricherà il pezzo e comunicherà alla macchina a valle che il pezzo è pronto
                    - PA4 --> il PLC triggera l'attuatore che scarterà il pezzo
                    - PA5 --> il PLC triggera la sirena della zona di controllo qualità
                    - MK4 --> scarico del pezzo alla macchina a valle
                    - MK5 --> scarto del pezzo in corso
                    - PE6 --> trigger al PLC che durante lo scarto/scarico del pezzo si sono riscontrati problemi
                    - PA6 --> il PLC triggera la sirena della zona di scarto/scarico
                    - MK6 --> il PLC viene triggerato dall'utente per comunicare che è stata ripristinare la condizione di failure (SCARICO/SCARTO)
                    - MK7 --> flusso di lavoro concluso
                """
                if self._PE[0] and not self._MK[0]:
                    # Il pezzo è stato caricato sul piano di lavoro e la lavorazione non è in corso e non ci sono errori
                    self._log.debug("Trigger to actuator to start processing routine...")
                    self._PA[0] = True
                
                if self._PA[0]:
                    # L'attuatore che deve far iniziare la lavorazione riceve il trigger
                    self._MK[0], self._PA[0] = True, False
                    threading.Thread(target=self.processing_routine).start()
                    self._log.debug("Processing...")
                
                if (self._PE[2] and not self._PA[2]) or (self._PE[5] and not self._PA[5]):
                    # Si è verificato un errore
                    if self._PE[2]:
                        self._log.warning("Error detected while processing!")
                        self._PA[2] = True # Trigger alla sirena della zona di lavorazione
                    else:
                        self._log.warning("Error detected while checking product quality")
                        self._PA[5] = True # Trigger alla sirena della zona di lavorazione
                
                if self._PA[2]:
                    self._log.error("OPERATOR NEEDED IN PROCESSING AREA!!")

                if self._PA[2] and self._PE[2] and self._MK[1]:
                    # L'utente comunica di aver ripristinato la situazione d'errore sul piano di lavorazione
                    self._log.debug("Problem resolved by the operator...")
                    self._PA[2], self._PE[2], self._MK[1], self._PE[0] = False, False, False, True
                    time.sleep(1)
                
                if self._PE[1] and not self._MK[2]:
                    # La lavorazione è andata a buon fine e si può avviare il processo di controllo qualità
                    self._log.debug("Trigger to actuator to start quality assurance routine...")
                    self._PA[1] = True

                if self._PA[1]:
                    # L'attuatore che deve far iniziare il processo di controllo qualità riceve il trigger
                    self._MK[2], self._PA[1] = True, False
                    threading.Thread(target=self.quality_assurance_routine).start()
                    self._log.debug("Checking product quality...")
                
                if self._PA[5]:
                    self._log.error("OPERATOR NEEDED IN QUALITY ASSURANCE AREA!!")

                if self._PA[5] and self._PE[5] and self._MK[3]:
                    # L'utente comunica di aver ripristinato la situazione d'errore nell'area di controllo qualità
                    self._log.debug("Problem resolved by the operator...")
                    self._PA[5], self._PE[5], self._MK[3], self._PE[0] = False, False, False, True
                    time.sleep(1)

                if self._PE[4] and not self._MK[5]:
                    # Il pezzo è da scartare
                    self._log.warning("Defected product, going to discard it...")
                    self._PA[4] = True
                
                if self._PA[4]:
                    # L'attuatore che deve scartare il pezzo riceve il trigger
                    self._MK[5], self._PA[4] = True, False
                    threading.Thread(target=self.discard_or_send_product, args = ["discard"]).start()
                    self._log.debug("Discarding product...")
                
                if self._PE[3] and not self._MK[4]:
                    # Il pezzo è buono e va mandato alla macchina a valle
                    self._log.debug("Product going to be sent to next machinery")
                    self._PA[3] = True

                if self._PA[3]:
                    # L'attuatore che deve scaricare il pezzo riceve il trigger
                    self._MK[4], self._PA[3] = True, False
                    threading.Thread(target=self.discard_or_send_product, args = ["send"]).start()
                    self._log.debug("Sending product...")

                if self._PE[6] and not self._PA[6]:
                    # Problemi durante lo scarico o lo scarto di un prodotto
                    self._log.warning("Error detected while sending/discarding the product")
                    self._PA[6] = True

                if self._PA[6]:
                    self._log.error("OPERATOR NEEDED IN SENDING/DISCARDING AREA")
                
                if self._PE[6] and self._PA[6] and self._MK[6]:
                    # L'utente comunica di aver ripristinato la situazione d'errore nell'area di scarico/scarto
                    self._log.debug("Problem resolved by the operator...")
                    self._PA[6], self._PE[6], self._MK[6], self._PE[0] = False, False, False, True
                    time.sleep(1)

                if self._MK[7]:
                    # Ciclo ultimato correttamente
                    self._log.debug("Cycle correctly ultimated, ready for the next.")
                    self._MK[7] = False

                # Attesa di 1 secondo prima del prossimo ciclo
                time.sleep(0.5)
        except KeyboardInterrupt:
            self._log.warning("Server manually blocked...")
        finally:
            self._server.stop()
            self._log.warning("Destroying server...")
            self._server.destroy()

if __name__ == '__main__':

    PLC = Siemens()
    PLC.run()