import snap7.server as srv
import snap7.types as tps
import time
import logging
import ctypes

logging.basicConfig(level=logging.INFO)

"""
Definiamo una classe Siemens che sostanzialmente sarà 
il nostro PLC Siemens che comunica mediante protocollo 
S7Comm (implementato dalla libreria snap7 per noi).
"""

class Siemens:

    _server: srv.Server
    
    def __init__(self, data_blocks = None):

        """
        Creiamo il server
        """
        logging.info("Creating server...")
        self._server = srv.Server(log=False)

        """
        I DB (Data_Block) sono le unità di memoria del PLC Siemens
        e noi diamo l'opportunità di personalizzarle in modo tale da 
        poter simulare il contesto più vicino alla realtà possibile
        """
        for i, db in enumerate(data_blocks):
            """
            Aggiungiamo il DB al PLC
            """
            logging.info(f"Adding DB number: {i+1}")
            ctype_array = (ctypes.c_ubyte * len(db)).from_buffer_copy(db)
            self._server.register_area(tps.srvAreaDB, i+1, ctype_array)

    def run(self):

        """
        Avviamo il server
        """
        logging.info("Starting server...")
        self._server.start()
        
        try:
            while True:
                event = self._server.pick_event()
                if event:
                    logging.info(f"Event found: {event}")

                # Attesa di 1 secondo prima del prossimo ciclo
                time.sleep(1)
        except KeyboardInterrupt:
            logging.info("Server manually arrested...")
        finally:
            self._server.stop()
            logging.info("Destroying server...")
            self._server.destroy()

if __name__ == '__main__':
    data_blocks = [
        bytearray(1024),
        bytearray(1024),
        bytearray(1024)
    ]
    PLC = Siemens(data_blocks=data_blocks)
    PLC.run()