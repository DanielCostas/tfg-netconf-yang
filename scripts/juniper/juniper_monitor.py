from ncclient import manager
import xml.dom.minidom
import datetime

# --- DATOS DE CONEXIÓN ---
HOST = '192.168.10.50'
PORT = 830
USER = 'root'
PASS = 'Telematica2026'
DEVICE_PARAMS = {'name': 'junos'}

def demo_monitor_backup():
    print(f"\n--- INICIANDO SISTEMA DE BACKUP Y MONITORIZACIÓN ---")
    
    try:
        with manager.connect(host=HOST, port=PORT, username=USER, password=PASS,
                             hostkey_verify=False, device_params=DEVICE_PARAMS,
                             look_for_keys=False, allow_agent=False) as m:

            # --- PARTE A: BACKUP AUTOMÁTICO ---
            print("\n1. [BACKUP] Descargando configuración completa 'Running'...")
            
            # get_config sin filtros trae TODO
            full_config = m.get_config(source='running')
            
            # Convertimos a string (Corrección del error anterior)
            config_xml = str(full_config)
            
            # Generamos nombre de archivo con fecha
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"backup_juniper_{timestamp}.xml"
            
            # Guardamos en disco
            with open(filename, 'w') as f:
                f.write(xml.dom.minidom.parseString(config_xml).toprettyxml())
                
            print(f"   [ÉXITO] Copia de seguridad guardada en: '{filename}'")

            # --- PARTE B: ESTADO OPERACIONAL (Monitorización) ---
            print("\n2. [MONITOR] Consultando estado físico de las interfaces (RPC get-interface-information)...")
            
            # En Juniper, para ver el estado físico (UP/DOWN) y tráfico, 
            # se usa una RPC específica llamada 'get-interface-information'
            # NETCONF permite ejecutar cualquier RPC nativa del fabricante.
            
            op_rpc = '<get-interface-information><terse/></get-interface-information>'
            
            result = m.rpc(op_rpc)
            
            # Parseamos para mostrar algo legible
            xml_str = str(result)
            dom = xml.dom.minidom.parseString(xml_str)
            
            # Extraemos nombres y estados (Una pequeña extracción manual para la demo)
            print("\n   --- RESUMEN DE ESTADO (LIVE) ---")
            interfaces = dom.getElementsByTagName("physical-interface")
            
            for iface in interfaces:
                name = iface.getElementsByTagName("name")[0].firstChild.data
                state = iface.getElementsByTagName("oper-status")[0].firstChild.data
                print(f"   INTERFACE: {name:<15} ESTADO: {state}")
                
            print("\n--- FIN DEL PROCESO ---")

    except Exception as e:
        print(f"[ERROR]: {e}")

if __name__ == '__main__':
    demo_monitor_backup()
