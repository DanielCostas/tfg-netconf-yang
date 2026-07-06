#!/bin/sh
# Script de inicialización y arranque manual de Clixon en OpenWrt

echo "1. Inicializando Datastore XML (running_db)..."
mkdir -p /usr/local/var/clixon
echo "<config/>" > /usr/local/var/clixon/running_db.xml

echo "2. Deteniendo instancias previas de Clixon..."
killall clixon_backend 2>/dev/null || true

echo "3. Arrancando el Backend de Clixon..."
/usr/sbin/clixon_backend -F -f /etc/clixon/clixon.xml -s init &

echo "4. Arrancando el subsistema NETCONF..."
/usr/bin/clixon_netconf -f /etc/clixon/clixon.xml -D 1 &

echo "Servicios de Clixon iniciados correctamente en segundo plano."
