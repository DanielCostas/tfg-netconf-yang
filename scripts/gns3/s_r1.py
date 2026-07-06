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
      <name>eth2</name>
      <type>ianaift:ethernetCsmacd</type>
      <enabled>true</enabled>
      <ipv4 xmlns="urn:ietf:params:xml:ns:yang:ietf-ip">
        <address>
          <ip>10.0.12.1</ip>
          <netmask>255.255.255.0</netmask>
        </address>
      </ipv4>
    </interface>

    <interface>
      <name>eth3</name>
      <type>ianaift:ethernetCsmacd</type>
      <enabled>true</enabled>
      <ipv4 xmlns="urn:ietf:params:xml:ns:yang:ietf-ip">
        <address>
          <ip>10.0.13.1</ip>
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
    print("Enviando configuración a R1...")
    response = m.edit_config(target="candidate", config=config_data)
    print("Haciendo commit...")
    m.commit()
    print("Configuración aplicada correctamente en R1.")
    print(response)
