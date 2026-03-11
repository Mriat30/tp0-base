#!/bin/bash
set -e

output_file="$1"
num_clients="$2"

if [ -z "$output_file" ] || [ -z "$num_clients" ]; then
    echo "Uso: ./generar-compose.sh <output_file> <num_clients>"
    exit 1
fi

echo "Nombre del archivo de salida: $output_file"
echo "Cantidad de clientes: $num_clients"

python3 mi-generador.py "$output_file" "$num_clients"
