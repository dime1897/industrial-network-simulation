import time
import loguru
import threading
import random as rnd
from pyModbusTCP.server import ModbusServer
from typing import Union

class Beckhoff:

    # Dettagli del PLC
    _server: ModbusServer

    # Failure rate
    _picking_area_failure_rate: float
    _releasing_area_failure_rate: float
    _plier_failure_rate: float

    # Arrival rate
    _product_arrival_rate: int
    _box_arrival_rate: int

    # Logger
    _log: None

    def __init__(self, host="localhost", port=10502): #502 È la porta di Modbus, ho messo la 10502 solo per non dover fare sudo tutte le volte
        
        # Crezione del server
        self._server = ModbusServer(host=host, port=port, no_block=True)

        # Settaggio dei failure rate
        self._picking_area_failure_rate = 0.0
        self._plier_failure_rate = 0.0
        self._releasing_area_failure_rate = 0.0

        # Settaggio dei tassi d'arrivo
        self._product_arrival_rate = 2 # Arrivano due prodotti al secondo sulla linea di prelievo
        self._box_arrival_rate = 0.33333 # Arriva una scatola ogni tre secondi circa (sincronizzato con l'arrivo dei prodotti)

        # Configurazione delle aree di memoria
        self._server.data_bank.set_coils(0, [False]*20) # 10 ingressi fisici; offset 0
        self._server.data_bank.set_coils(10, [False]*10) # 10 uscite fisiche; offset 10
        self._server.data_bank.set_holding_registers(20, [0]*10) # 10 registri di holding Merker; offset 20
        self._server.data_bank.set_holding_registers(30, [100, 200, 300, 400]) # 4 registri di holding per i DB; offset 30 

        # Configurazione del logger
        self._log = loguru.logger

        self._log.debug("Server configuration ended...")

    def set_coils(self, start_address:int, values:list):
        self._server.data_bank.set_coils(start_address, values)

    def get_coils(self, start_address:int, number:int):
        #self._log.debug(f"Called with:\nstart_address={start_address}\nnumber={number}\nReading:{self._server.data_bank.get_coils(start_address, number)}")
        return self._server.data_bank.get_coils(start_address, number)

    def product_arriving(self):
        
        if rnd.random() < self._picking_area_failure_rate:
            # Un prodotto è caduto mentre arrivava
            self.set_coils(7, [True]) # Triggeriamo l'errore senza cambiare lo stato perché i prodotti che c'erano già restano
            return

        state = self.get_coils(0, 6)
        self._log.debug("2 products arrived...")
        if state == [False,False,False,False,False,False]:
            self.set_coils(0, [True, True]) # I primi due prodotti sono arrivati
        elif state == [True,True,False,False,False,False]:
            self.set_coils(2, [True, True]) # La seconda coppia di prodotti è arrivata
        elif state == [True,True,True,True,False,False]:
            self.set_coils(4, [True, True]) # La terza coppia di prodotti è arrivata
        elif state == [True,True,True,True,True,True]:
            self.set_coils(10, [True]) # Tiriamo su la barriera perché la stazione di prelievo è piena
            self._log.warning("Picking station full...")

    def box_arriving(self):

        self.set_coils(6, [True]) # Triggeriamo la presenza della scatola
        self._log.debug("Box arrived...")

    def filling_process(self):

        if rnd.random() < self._plier_failure_rate:
            # La pinza ha riscontrato un problema
            self.set_coils(8, [True]) # In questo caso il problema alla pinza è nato prima di agganciare i prodotti
            return

        # Per simulare il riempimento useremo alcune sleep e cambieremo lo stato dei bit coerentemente a quanto succede
        self.set_coils(11, [True]) # Posizioniamo il braccio meccanico sulla stazione di prelievo e lo simuliamo con 1s di sleep
        self._log.debug("Positioning above picking station...")
        time.sleep(1)

        self.set_coils(12, [True])
        self._log.debug("Tightening the plier...")
        time.sleep(1)

        self.set_coils(11, [False, True, True]) # Posizioniamo il braccio meccanico sulla stazione di prelievo e lo simuliamo con 1s di sleep
        self._log.debug("Moving above releasing station...")
        self.set_coils(0, [False]*6)
        if self.get_coils(10,1)[0]:
            self.set_coils(10,[False]) # Se la barriera era alta la riabbassiamo
        if rnd.random() < self._plier_failure_rate:
            # La pinza ha riscontrato un problema
            self.set_coils(8, [True]) # In questo caso il problema alla pinza è nato durante lo spostamento, quindi si perde la presa
            self.set_coils(11, [False,False])
            return
        time.sleep(1)

        self.set_coils(12, [False, True]) # Lasciamo il prodotto all'interno della scatola
        self._log.debug("Releasing product...")
        if rnd.random() < self._releasing_area_failure_rate:
            # Problemi nell'area di rilascio
            self.set_coils(13, [False])
            self.set_coils(9, [True])
            return
        time.sleep(1)

        self.set_coils(13, [False]) # Posizioniamo il braccio in home
        self.set_coils(6, [False]) # Resettiamo bit di presenza scatola
        self._log.debug("Moving back to home station...")


    def run(self):
        
        self._server.start()
        self._log.debug("Server started...")

        try:
            cnt=0 # Per contare i 3 secondi dopo cui arriverà la scatola
            while True:
                """
                Nella logica di controllo di questo PLC vogliamo andare a prelevare N oggetti (nel nostro caso 6)
                da una linea di arrivo di prodotti, per posizionarli all'interno di un apposito contenitore (che dovrà
                essere presente sull'apposita linea).
                Dunque faremo uso di:
                    - 0-5 --> ingresso TRUE se il prodotto è presente nella rispettiva stazione di prelievo, FALSE altrimenti
                    - 6 --> ingresso TRUE se la scatola da riempire è presente sulla stazione di rilascio
                    - 7 --> ingresso TRUE se si sono verificati problemi sulla stazione di prelievo (prodotto caduto o barriera bloccata ad esempio), FALSE altrimenti
                    - 8 --> ingresso TRUE se si sono verificati problemi sul braccio meccanico (incastrato, presa a vuoto o prodotto perso ad esempio), FALSE altrimenti
                    - 9 --> ingresso TRUE se si sono verificati problemi sulla stazione di rilascio (prodotto caduto o scatola difettata ad esempio), FALSE altrimenti
                    - 10 --> uscita TRUE quando è alta la barriera che ferma i prodotti quando la stazione di prelievo è piena, FALSE altrimenti
                    - 11 --> uscita TRUE quando si vuole posizionare il braccio meccanico sulla stazione di prelievo, FALSE altrimenti
                    - 12 --> uscita TRUE quando si vuole stringere le pinze per afferrare il prodotto, FALSE altrimenti
                    - 13 --> uscita TRUE quando si vuole posizionare il braccio meccanico sulla stazione di rilascio, FALSE altrimenti
                    - 14 --> uscita TRUE quando si vuole chiudere la scatola, FALSE altrimenti
                Una volta chiusa la scatola il ciclo termina ed assumiamo che il braccio meccanico torni in posizione di home automaticamente senza doverlo gestire.
                Per semplicità assumiamo che al verificarsi di un errore, l'utente mediante l'HMI vada direttamente a porre FALSE il bit riguardante l'errore.
                """
                cnt += 1

                if (cnt*self._box_arrival_rate) >= 0.99:
                    # Dobbiamo far arrivare la scatola se non c'è già
                    if not self.get_coils(6,1)[0]: 
                        # Se non c'è già la scatola
                        threading.Thread(target=self.box_arriving).start()
                    cnt = 0 # Ricominciamo il conteggio

                if not self.get_coils(7,1)[0] and not self.get_coils(8,1)[0] and not self.get_coils(9,1)[0] and not self.get_coils(10,1)[0]:
                    # Ogni secondo arrivano due prodotti se non ci sono errori e se non c'è la barriera alta
                    threading.Thread(target=self.product_arriving).start()
                
                if self.get_coils(7,1)[0]:
                    # Si è verificato un problema sulla stazione di prelievo
                    self._log.error("OPERATOR NEEDED IN PICKING AREA!!!")

                if self.get_coils(0,6) == [True,True,True,True,True,True] and self.get_coils(6, 1)[0] and self.get_coils(11, 3) == [False, False, False]:
                    # La stazione di prelievo è piena e possiamo riempire
                    threading.Thread(target=self.filling_process).start()

                if self.get_coils(8,1)[0]:
                    # Si è verificato un problema sulla stazione di prelievo
                    self._log.error("OPERATOR NEEDED BY THE PLIER!!!")

                if self.get_coils(9,1)[0]:
                    # Si è verificato un problema sulla stazione di prelievo
                    self._log.error("OPERATOR NEEDED IN RELEASING AREA!!!")

                # Attesa di 1 secondo prima del prossimo ciclo
                time.sleep(1)
        except KeyboardInterrupt:
            self._log.warning("Server manually blocked...")
        finally:
            self._server.stop()
            self._log.warning("Destroying server...")

if __name__ == "__main__":
    PLC = Beckhoff()
    PLC.run()