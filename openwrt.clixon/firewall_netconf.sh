#!/bin/sh
# Configuración de Seguridad: Cortafuegos de OpenWrt
# Permite el acceso de gestión NETCONF/SSH desde el Host anfitrión hacia la zona WAN

echo "Configurando reglas del cortafuegos para NETCONF (Puerto 22)..."

uci add firewall rule
uci set firewall.@rule[-1].name='Allow-SSH-from-Host'
uci set firewall.@rule[-1].src='wan'
uci set firewall.@rule[-1].dest_port='22'
uci set firewall.@rule[-1].proto='tcp'
uci set firewall.@rule[-1].target='ACCEPT'
uci commit firewall

echo "Reiniciando el cortafuegos..."
/etc/init.d/firewall restart
echo "Acceso NETCONF/SSH habilitado."
