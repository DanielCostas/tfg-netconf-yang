from ncclient import manager

# Conexión a R3 a través del túnel SSH
HOST = "localhost"
PORT = 2223  # puerto local del túnel hacia R3
USER = "root"
PASSWORD = "telematica"

config_data = """
<config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces"
              xmlns:ianaift="urn:ietf:params:xml:ns:yang:iana-if-type">

    <!-- Configuración de eth1 hacia R2 -->
    <interface>
      <name>eth1</name>
      <type>ianaift:ethernetCsmacd</type>
      <enabled>true</enabled>
      <ipv4 xmlns="urn:ietf:params:xml:ns:yang:ietf-ip">
        <address>
          <ip>10.0.13.3</ip>
          <netmask>255.255.255.0</netmask>
        </address>
      </ipv4>
    </interface>

    <!-- Configuración de eth2 hacia R1 -->
    <interface>
      <name>eth2</name>
      <type>ianaift:ethernetCsmacd</type>
      <enabled>true</enabled>
      <ipv4 xmlns="urn:ietf:params:xml:ns:yang:ietf-ip">
        <address>
          <ip>10.0.23.3</ip>
          <netmask>255.255.255.0</netmask>
        </address>
      </ipv4>
    </interface>

  </interfaces>
</config>
"""

with manager.connect(
    host=HOST,
    port=PORT,
    username=USER,
    password=PASSWORD,
    hostkey_verify=False,
    allow_agent=False,
    look_for_keys=False
) as m:
    print("Enviando configuración a R3...")
    response = m.edit_config(target="candidate", config=config_data)
    print("Haciendo commit...")
    m.commit()
    print("Configuración aplicada correctamente en R3.")
    print(response)
