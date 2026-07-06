# Gestión y Automatización de Redes mediante NETCONF y modelos YANG

Este repositorio contiene el código y los procedimientos desarrollados para la automatización de redes en entornos híbridos (virtuales y físicos) mediante el protocolo NETCONF y modelos YANG. 

## Arquitectura del Proyecto

El proyecto se divide en los siguientes componentes tecnológicos:
- **Entorno Virtual**: Topología en GNS3 utilizando enrutadores OpenWrt junto con el framework Clixon.
- **Entorno Físico**: Configuración, auditoría y pruebas de resiliencia sobre un switch Juniper EX4200 de grado industrial.
- **Demonio `uci_sync`**: Desarrollo en lenguaje C para solventar la brecha entre el framework Clixon (YANG) y OpenWrt (UCI), sincronizando las configuraciones en tiempo real y aplicando los cambios al kernel.
- **Orquestación**: Scripts de Python utilizando la librería `ncclient` para establecer sesiones seguras y actuar como controlador SDN.

## Estructura del Repositorio

- `/OpenWrt.Clixon`: Códigos Desarrollados para la correcta implementación tanto de OpenWrt como Clixon.
- `/scripts/`: Scripts de Python orientados a la ingeniería de tráfico y a la gestión del hardware Juniper.

## Autor
Daniel Costas San Miguel
