from ncclient import manager
from ncclient.xml_ import to_ele
import time
import sys

# --- DATOS DE CONEXIÓN ---
HOST = '192.168.10.50'
PORT = 830
USER = 'root'
PASS = 'Telematica2026'
# Recordamos usar 'junos' que es el que te funcionó
DEVICE_PARAMS = {'name': 'junos'}

def demo_rollback():
    print(f"\n--- INICIANDO SIMULACIÓN DE FALLO Y ROLLBACK ---")
    
    with manager.connect(host=HOST, port=PORT, username=USER, password=PASS,
                         hostkey_verify=False, device_params=DEVICE_PARAMS,
                         look_for_keys=False, allow_agent=False) as m:

        # --- FASE 1: PROVOCAR EL ERROR ---
        print("\n1. [ACCIÓN] Introduciendo configuración 'errónea'...")
        
        bad_hostname = "ERROR-CRITICO-SISTEMA"
        bad_config = f"""
        <config>
            <configuration>
                <system>
                    <host-name>{bad_hostname}</host-name>
                </system>
            </configuration>
        </config>
        """
        
        with m.locked(target='candidate'):
            m.edit_config(target='candidate', config=bad_config)
            m.commit()
            print(f"   [ALERTA] Hostname cambiado a '{bad_hostname}'.")
            print("   (Mira la pantalla del Minicom/Switch ahora mismo)")

        # --- FASE 2: TIEMPO DE ESPERA (DRAMATISMO) ---
        print("\n2. [ESPERA] Pausando 10 segundos para verificar el error...")
        for i in range(10, 0, -1):
            print(f"   Restaurando en {i}...", end='\r')
            time.sleep(1)
        print("\n")

        # --- FASE 3: EJECUTAR ROLLBACK ---
        print("3. [RECUPERACIÓN] Ejecutando 'Rollback 1' (Volver al estado anterior)...")
        
        # En NETCONF para Juniper, el rollback se carga como una RPC especial
        # <load-configuration rollback="1"/>
        rollback_rpc = '<load-configuration rollback="1"/>'
        
        with m.locked(target='candidate'):
            # Enviamos la RPC cruda al dispositivo
            m.rpc(to_ele(rollback_rpc))
            print("   [INFO] Configuración anterior cargada en 'candidate'.")
            
            # ¡IMPORTANTE! El rollback solo carga el borrador, hay que hacer commit
            print("   [ACCIÓN] Aplicando recuperación (COMMIT)...")
            m.commit()
            print("   [ÉXITO] Sistema restaurado correctamente.")

if __name__ == '__main__':
    demo_rollback()
