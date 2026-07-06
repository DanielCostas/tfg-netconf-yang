from ncclient import manager

# Conexión a R2 a través del túnel SSH
HOST = "localhost"
PORT = 2222  # puerto local del túnel hacia R2
USER = "root"
PASSWORD = "telematica"

config_data = """
<config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces"
              xmlns:ianaift="urn:ietf:params:xml:ns:yang:iana-if-type">

    <!-- Configuración de eth1 hacia R1 -->
    <interface>
      <name>eth1</name>
      <type>ianaift:ethernetCsmacd</type>
      <enabled>true</enabled>
      <ipv4 xmlns="urn:ietf:params:xml:ns:yang:ietf-ip">
        <address>
          <ip>10.0.12.2</ip>
          <netmask>255.255.255.0</netmask>
        </address>
      </ipv4>
    </interface>

    <!-- Configuración de eth3 hacia R3 -->
    <interface>
      <name>eth3</name>
      <type>ianaift:ethernetCsmacd</type>
      <enabled>true</enabled>
      <ipv4 xmlns="urn:ietf:params:xml:ns:yang:ietf-ip">
        <address>
          <ip>10.0.23.2</ip>
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
    print("Enviando configuración a R2...")
    response = m.edit_config(target="candidate", config=config_data)
    print("Haciendo commit...")
    m.commit()
    print("Configuración aplicada correctamente en R2.")
    print(response)
