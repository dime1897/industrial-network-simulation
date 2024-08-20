from pyModbusTCP.server import ModbusServer
import loguru

class Beckhoff:

    _server: ModbusServer

    _log: None

    def __init__(self, host="localhost", port=10502): #502 È la porta di Modbus, ho messo la 10502 solo per non dover fare sudo tutte le volte
        
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
        
        self._server.start()
        self._log.debug("Server started...")

        try:
            while True:
                """
                Nella logica di controllo di questo PLC a noi interessa ricevere dal macchnario a valle
                """
                pass
        except KeyboardInterrupt:
            self._log.warning("Server stopped...")
        finally:
            self._server.stop()

if __name__ == "__main__":
    PLC = Beckhoff()
    PLC.run()