from ncclient import manager
import xml.dom.minidom

# --- DATOS DE CONEXIÓN ---
HOST = '192.168.10.50'
PORT = 830
USER = 'root'
PASS = 'Telematica2026'
DEVICE_PARAMS = {'name': 'junos'}

def demo_filtering():
    print(f"\n--- INICIANDO DEMOSTRACIÓN DE FILTRADO (SUBTREE FILTERING) ---")
    
    with manager.connect(host=HOST, port=PORT, username=USER, password=PASS,
                         hostkey_verify=False, device_params=DEVICE_PARAMS,
                         look_for_keys=False, allow_agent=False) as m:

        # --- DEFINICIÓN DEL FILTRO ---
        # Queremos solo la configuración de las interfaces
        filter_payload = """
        <filter type="subtree">
            <configuration>
                <interfaces/>
            </configuration>
        </filter>
        """

        print("\n1. [SOLICITUD] Pidiendo al switch SOLO la configuración de interfaces...")
        
        # Ejecutamos get_config aplicando el filtro
        reply = m.get_config(source='running', filter=filter_payload)
        
        print("   [OK] Datos recibidos.")
        
        # --- PROCESADO Y VISUALIZACIÓN ---
        print("\n2. [RESULTADO] XML Filtrado (Muestra parcial):")
        
        # --- CORRECCIÓN AQUÍ ---
        # Usamos str(reply) porque 'reply' ya es un elemento XML de Junos
        xml_string = str(reply)
        
        # Parseamos el XML para que se lea bien (Pretty Print)
        xml_doc = xml.dom.minidom.parseString(xml_string)
        pretty_xml = xml_doc.toprettyxml()
        
        # Imprimimos el resultado (Solo los primeros 1000 caracteres para no llenar la pantalla)
        print("-" * 40)
        print(pretty_xml[:1000] + "\n\n... [resto del XML oculto] ...")
        print("-" * 40)
        
        # Verificación simple para el TFG
        if "<interfaces>" in xml_string:
            print("\n[CONCLUSIÓN] El filtrado ha funcionado: Hemos recibido datos de <interfaces>.")
        else:
            print("\n[ATENCIÓN] No se encontró la etiqueta <interfaces>. Revisa el filtro.")

if __name__ == '__main__':
    demo_filtering()
