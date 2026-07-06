from ncclient import manager

HOST = "192.168.122.165"
PORT = 22
USER = "root"
PASSWORD = "telematica"

config_data = """
<config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">

  <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces"
              xmlns:ianaift="urn:ietf:params:xml:ns:yang:iana-if-type">
    <interface>
      <name>eth3</name>
      <type>ianaift:ethernetCsmacd</type>
      <enabled>true</enabled>
    </interface>
  </interfaces>

  <routing xmlns="urn:ietf:params:xml:ns:yang:ietf-routing"
           xmlns:v4ur="urn:ietf:params:xml:ns:yang:ietf-ipv4-unicast-routing">
    <control-plane-protocols>
      <control-plane-protocol>
        <type>static</type>
        <name>static-routing-main</name>
        <static-routes>
          <v4ur:ipv4>
            <v4ur:route>
              <v4ur:destination-prefix>10.0.23.0/24</v4ur:destination-prefix>
              
              <v4ur:description>GW:10.0.13.3</v4ur:description>
              
              <v4ur:next-hop>
                <v4ur:outgoing-interface>eth3</v4ur:outgoing-interface>
              </v4ur:next-hop>
            </v4ur:route>
          </v4ur:ipv4>
        </static-routes>
      </control-plane-protocol>
    </control-plane-protocols>
  </routing>
</config>
"""

with manager.connect(host=HOST, port=PORT, username=USER, password=PASSWORD,
                     hostkey_verify=False, allow_agent=False, look_for_keys=False) as m:
    print("Enviando ruta R1->R3 (Formato uci_sync)...")
    try:
        m.edit_config(target="candidate", config=config_data)
        m.commit()
        print("¡Configuración aceptada por Netconf!")
    except Exception as e:
        print(f"Error: {e}")
