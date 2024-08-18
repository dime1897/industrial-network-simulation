import snap7.client as c
from snap7.util import *
from snap7.types import *

def write_and_read_PA(client):
    # Scrittura e lettura dell'area PA (Process Output Area)
    print("Scrittura e lettura dell'area PA (Process Output Area):")
    
    # Scrittura: Setto il bit 0 del primo byte dell'area PA a True
    pa_data = (ctypes.c_uint8 * 1)()
    set_bool(pa_data, 0, 0, True)
    client.write_area(Areas.PA, 0, 0, pa_data)
    
    # Lettura: Leggo il primo byte dell'area PA
    read_pa = client.read_area(Areas.PA, 0, 0, 1)
    print(f"Valore del bit 0 di PA0.0: {get_bool(read_pa, 0, 0)}")

def write_and_read_PE(client):
    # Scrittura e lettura dell'area PE (Process Input Area)
    print("Scrittura e lettura dell'area PE (Process Input Area):")
    
    # Scrittura: Setto il bit 0 del primo byte dell'area PE a True
    pe_data = (ctypes.c_uint8 * 1)()
    set_bool(pe_data, 0, 0, True)
    client.write_area(Areas.PE, 0, 0, pe_data)
    
    # Lettura: Leggo il primo byte dell'area PE
    read_pe = client.read_area(Areas.PE, 0, 0, 1)
    print(f"Valore del bit 0 di PE0.0: {get_bool(read_pe, 0, 0)}")

def write_and_read_MK(client):
    # Scrittura e lettura dell'area MK (Merker Area)
    print("Scrittura e lettura dell'area MK (Merker):")
    
    # Scrittura: Setto il bit 0 del primo byte dell'area MK a True
    mk_data = (ctypes.c_uint8 * 1)()
    set_bool(mk_data, 0, 0, True)
    client.write_area(Areas.MK, 0, 0, mk_data)
    
    # Lettura: Leggo il primo byte dell'area MK
    read_mk = client.read_area(Areas.MK, 0, 0, 1)
    print(f"Valore del bit 0 di MK0.0: {get_bool(read_mk, 0, 0)}")

def write_and_read_DB(client, db_number):
    # Scrittura e lettura dei Data Block
    print(f"Scrittura e lettura del Data Block {db_number}:")
    
    # Scrittura: Setto il bit 0 del primo byte del Data Block a True
    db_data = (ctypes.c_uint8 * 1)()
    set_bool(db_data, 0, 0, True)
    client.write_area(Areas.DB, db_number, 0, db_data)
    
    # Lettura: Leggo il primo byte del Data Block
    read_db = client.read_area(Areas.DB, db_number, 0, 1)
    print(f"Valore del bit 0 di DB{db_number}.0: {get_bool(read_db, 0, 0)}")

def main():
    # Creazione del client Snap7
    client = c.Client()

    # Connessione al server (ad esempio, su localhost e porta 102)
    client.connect('127.0.0.1', 0, 1, 22000)
    
    # Verifica connessione
    if client.get_connected():
        print("Connessione stabilita con il PLC simulato.\n")
    else:
        print("Errore nella connessione al PLC simulato.")
        return

    # Scrittura e lettura di tutte le aree registrate
    #write_and_read_PA(client)
    write_and_read_PE(client)
    #write_and_read_MK(client)
#
    ## Scrittura e lettura dei Data Blocks
    #for i in range(10):  # Per ogni DB dal 1 al 8 (come configurato nel server)
    #    write_and_read_DB(client, i)

    # Disconnessione dal server
    client.disconnect()
    print("\nDisconnessione dal PLC simulato avvenuta con successo.")

if __name__ == '__main__':
    main()

