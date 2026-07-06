from ncclient import manager

# --- CONFIGURACIÓN DE CONEXIÓN (Out-of-Band) ---
HOST = "192.168.10.50"
PORT = 830
USER = "root"
PASS = "Telematica2026"
DEVICE_PARAMS = {'name': 'junos'}

def audit_capabilities():
    print(f"\n--- AUDITORÍA DE CAPACIDADES: {HOST} ---")
    print("Conectando vía interfaz de gestión (vme)...")
    
    try:
        with manager.connect(host=HOST, port=PORT, username=USER, password=PASS,
                             hostkey_verify=False, device_params=DEVICE_PARAMS,
                             look_for_keys=False, allow_agent=False) as m:
            
            print("[OK] Conexión establecida.\n")
            print("LISTADO DE CAPACIDADES DEL SERVIDOR:")
            print("=" * 60)
            
            # Bucle simple para listar todo sin filtros
            for capability in m.server_capabilities:
                print(capability)

            print("=" * 60)
            print("\n[FIN DE LA AUDITORÍA]")

    except Exception as e:
        print(f"\n[ERROR] No se pudo conectar: {e}")

if __name__ == '__main__':
    audit_capabilities()
