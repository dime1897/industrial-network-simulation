from pyModbusTCP.server import ModbusServer
import loguru

class Beckhoff():

    _server: ModbusServer

    _log: None

    def __init__(self, host="localhost", port=23000):
        
        # Configurazione del server
        self._server = ModbusServer(host=host, port=port, no_block=True)

        # Configurazione delle aree di memoria
        self._server.data_bank.set_coils(0, [False]*10) # 10 ingressi fisici; offset 0
        self._server.data_bank.set_coils(10, [False]*10) # 10 uscite fisiche; offset 10
        self._server.data_bank.set_holding_registers(20, [0]*10) # 10 registri di holding Merker; offset 20
        self._server.data_bank.set_holding_registers(30, [100, 200, 300, 400]) # 4 registri di holding per i DB; offset 30 

        # Configurazione del logger
        self._log = loguru.logger

        self._log.debug("Server configuration ended...")

    def run(self):
        
        try:
            self._server.start()
            self._log.debug("Server started...")

            while True:
                        # Il server continua a girare finché non viene interrotto
                        pass
        except KeyboardInterrupt:
            self._log.warning("Server stopped.")
        finally:
            self._server.stop()

if __name__ == "__main__":
    PLC = Beckhoff()
    PLC.run()