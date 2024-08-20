from pyModbusTCP.client import ModbusClient
import time

# Configura il client
client = ModbusClient(host="localhost", port=23000, auto_open=True)

def read_coils(start_address, quantity):
    """Legge una serie di coils dal server."""
    coils = client.read_coils(start_address, quantity)
    if coils is None:
        print(f"Failed to read coils from address {start_address}")
    else:
        print(f"Coils at address {start_address}: {coils}")

def write_coil(address, value):
    """Scrive un valore su un coil specifico."""
    success = client.write_single_coil(address, value)
    if not success:
        print(f"Failed to write coil at address {address}")
    else:
        print(f"Successfully wrote {value} to coil at address {address}")

def read_holding_registers(start_address, quantity):
    """Legge una serie di coils dal server."""
    hr = client.read_holding_registers(start_address, quantity)
    if hr is None:
        print(f"Failed to read holding registers from address {start_address}")
    else:
        print(f"Holding registers at address {start_address}: {hr}")

def main():
    # Esempio di lettura e scrittura di coils
    try:
        # Leggi coils
        read_coils(0, 3)  # Legge 3 coils a partire dall'indirizzo 0
        read_holding_registers(20, 3)
        read_holding_registers(30, 4)

        # Scrivi un valore su un coil
        #write_coil(0, True)
        #write_coil(1, True)  # Imposta il coil all'indirizzo 1 a True
        #write_coil(2, False) # Imposta il coil all'indirizzo 2 a False

        # Attendi un po' di tempo per vedere l'effetto
        time.sleep(2)

        # Leggi di nuovo i coils
        read_coils(0, 3)  # Legge 3 coils a partire dall'indirizzo 0

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
