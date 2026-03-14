#!/bin/bash

SERVER_PORT=12345
SERVER_IP=server
NETWORK=tp0_testing_net
MENSAJE="Mensaje de test"

if [ -z "$SERVER_PORT" ] || [ -z "$SERVER_IP" ]; then
    echo "Error: No se pudo leer SERVER_IP o SERVER_PORT de server/config.ini"
    exit 1
fi

RESPUESTA=$(echo "$MENSAJE" | docker run -i --rm --network $NETWORK busybox nc -w 2 "$SERVER_IP" "$SERVER_PORT")
RESPUESTA_LIMPIA=$(echo "$RESPUESTA" | tr -d '\r')

if [ "$RESPUESTA_LIMPIA" = "$MENSAJE" ]; then
    echo "action: test_echo_server | result: success"
else
    echo "action: test_echo_server | result: fail"
fi
