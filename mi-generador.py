import sys

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 mi-generador.py <output_file> <num_clients>")
        sys.exit(1)

    output_file = sys.argv[1]
    try:
        num_clients = int(sys.argv[2])
    except ValueError:
        print("Error: num_clients must be an integer.")
        sys.exit(1)

    content = [
        "name: tp0",
        "services:",
        "  server:",
        "    container_name: server",
        "    image: server:latest",
        "    volumes:",
        "      - ./server/config.ini:/config.ini:ro",
        "    entrypoint: python3 /main.py",
        "    environment:",
        "      - PYTHONUNBUFFERED=1",
        f"      - N_CLIENTS={num_clients}",
        "    networks:",
        "      - testing_net",
        ""
    ]

    for i in range(1, num_clients + 1):
        content.append(f"  client{i}:")
        content.append(f"    container_name: client{i}")
        content.append(f"    image: client:latest")
        content.append(f"    env_file:")
        content.append(f"      - ./una_apuesta.env")
        content.append(f"    volumes:")
        content.append(f"      - ./client/config.yaml:/config.yaml:ro")
        content.append(f"      - ./.data/agency-{i}.csv:/data/agency-{i}.csv:ro")
        content.append(f"    entrypoint: /client")
        content.append(f"    environment:")
        content.append(f"      - CLI_ID={i}")
        content.append(f"    networks:")
        content.append(f"      - testing_net")
        content.append(f"    depends_on:")
        content.append(f"      - server")
        content.append("")

    content.extend([
        "networks:",
        "  testing_net:",
        "    ipam:",
        "      driver: default",
        "      config:",
        "        - subnet: 172.25.125.0/24"
    ])

    try:
        with open(output_file, 'w') as f:
            for line in content:
                f.write(line + "\n")
        print(f"Éxito: Archivo '{output_file}' generado correctamente.")
    except OSError as e:
        print(f"Error: No se pudo escribir en el archivo '{output_file}': {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()