# TP0: Docker + Comunicaciones + Concurrencia

## Introduccion

 El cliente (Golang) y el servidor (Python) fueron desarrollados en diferentes lenguajes simplemente para mostrar cómo dos lenguajes de programación pueden convivir en el mismo proyecto con la ayuda de containers, en este caso utilizando [Docker Compose](https://docs.docker.com/compose/).

## Indice

- [Instrucciones de uso](#instrucciones-de-uso)
	- [Servidor](#servidor)
	- [Cliente](#cliente)
	- [Ejemplo](#ejemplo)
- [Parte 1: Introducción a Docker](#parte-1-introduccion-a-docker)
	- [Ejercicio N°1](#ejercicio-1)
	- [Ejercicio N°2](#ejercicio-2)
	- [Ejercicio N°3](#ejercicio-3)
	- [Ejercicio N°4](#ejercicio-4)
- [Parte 2: Repaso de Comunicaciones](#parte-2-repaso-de-comunicaciones)
	- [Ejercicio N°5](#ejercicio-5)
	- [Ejercicio N°6](#ejercicio-6)
	- [Ejercicio N°7](#ejercicio-7)
- [Parte 3: Repaso de Concurrencia](#parte-3-repaso-de-concurrencia)
	- [Ejercicio N°8](#ejercicio-8)
- [Condiciones de Entrega](#condiciones-de-entrega)


<a id="instrucciones-de-uso"></a>
## Instrucciones de uso
El repositorio cuenta con un **Makefile** que incluye distintos comandos en forma de targets. Los targets se ejecutan mediante la invocación de:  **make \<target\>**. Los target imprescindibles para iniciar y detener el sistema son **docker-compose-up** y **docker-compose-down**, siendo los restantes targets de utilidad para el proceso de depuración.

Los targets disponibles son:

| target  | accion  |
|---|---|
|  `docker-compose-up`  | Inicializa el ambiente de desarrollo. Construye las imágenes del cliente y el servidor, inicializa los recursos a utilizar (volúmenes, redes, etc) e inicia los propios containers. |
| `docker-compose-down`  | Ejecuta `docker-compose stop` para detener los containers asociados al compose y luego  `docker-compose down` para destruir todos los recursos asociados al proyecto que fueron inicializados. Se recomienda ejecutar este comando al finalizar cada ejecución para evitar que el disco de la máquina host se llene de versiones de desarrollo y recursos sin liberar. |
|  `docker-compose-logs` | Permite ver los logs actuales del proyecto. Acompañar con `grep` para lograr ver mensajes de una aplicación específica dentro del compose. |
| `docker-image`  | Construye las imágenes a ser utilizadas tanto en el servidor como en el cliente. Este target es utilizado por **docker-compose-up**, por lo cual se lo puede utilizar para probar nuevos cambios en las imágenes antes de arrancar el proyecto. |
| `build` | Compila la aplicación cliente para ejecución en el _host_ en lugar de en Docker. De este modo la compilación es mucho más veloz, pero requiere contar con todo el entorno de Golang y Python instalados en la máquina _host_. |

<a id="servidor"></a>
### Servidor

Se trata de un "echo server", en donde los mensajes recibidos por el cliente se responden inmediatamente y sin alterar. 

Se ejecutan en bucle las siguientes etapas:

1. Servidor acepta una nueva conexión.
2. Servidor recibe mensaje del cliente y procede a responder el mismo.
3. Servidor desconecta al cliente.
4. Servidor retorna al paso 1.


<a id="cliente"></a>
### Cliente
 se conecta reiteradas veces al servidor y envía mensajes de la siguiente forma:
 
1. Cliente se conecta al servidor.
2. Cliente genera mensaje incremental.
3. Cliente envía mensaje al servidor y espera mensaje de respuesta.
4. Servidor responde al mensaje.
5. Servidor desconecta al cliente.
6. Cliente verifica si aún debe enviar un mensaje y si es así, vuelve al paso 2.

<a id="ejemplo"></a>
### Ejemplo

Al ejecutar el comando `make docker-compose-up`  y luego  `make docker-compose-logs`, se observan los siguientes logs:

```
client1  | 2024-08-21 22:11:15 INFO     action: config | result: success | client_id: 1 | server_address: server:12345 | loop_amount: 5 | loop_period: 5s | log_level: DEBUG
client1  | 2024-08-21 22:11:15 INFO     action: receive_message | result: success | client_id: 1 | msg: [CLIENT 1] Message N°1
server   | 2024-08-21 22:11:14 DEBUG    action: config | result: success | port: 12345 | listen_backlog: 5 | logging_level: DEBUG
server   | 2024-08-21 22:11:14 INFO     action: accept_connections | result: in_progress
server   | 2024-08-21 22:11:15 INFO     action: accept_connections | result: success | ip: 172.25.125.3
server   | 2024-08-21 22:11:15 INFO     action: receive_message | result: success | ip: 172.25.125.3 | msg: [CLIENT 1] Message N°1
server   | 2024-08-21 22:11:15 INFO     action: accept_connections | result: in_progress
server   | 2024-08-21 22:11:20 INFO     action: accept_connections | result: success | ip: 172.25.125.3
server   | 2024-08-21 22:11:20 INFO     action: receive_message | result: success | ip: 172.25.125.3 | msg: [CLIENT 1] Message N°2
server   | 2024-08-21 22:11:20 INFO     action: accept_connections | result: in_progress
client1  | 2024-08-21 22:11:20 INFO     action: receive_message | result: success | client_id: 1 | msg: [CLIENT 1] Message N°2
server   | 2024-08-21 22:11:25 INFO     action: accept_connections | result: success | ip: 172.25.125.3
server   | 2024-08-21 22:11:25 INFO     action: receive_message | result: success | ip: 172.25.125.3 | msg: [CLIENT 1] Message N°3
client1  | 2024-08-21 22:11:25 INFO     action: receive_message | result: success | client_id: 1 | msg: [CLIENT 1] Message N°3
server   | 2024-08-21 22:11:25 INFO     action: accept_connections | result: in_progress
server   | 2024-08-21 22:11:30 INFO     action: accept_connections | result: success | ip: 172.25.125.3
server   | 2024-08-21 22:11:30 INFO     action: receive_message | result: success | ip: 172.25.125.3 | msg: [CLIENT 1] Message N°4
server   | 2024-08-21 22:11:30 INFO     action: accept_connections | result: in_progress
client1  | 2024-08-21 22:11:30 INFO     action: receive_message | result: success | client_id: 1 | msg: [CLIENT 1] Message N°4
server   | 2024-08-21 22:11:35 INFO     action: accept_connections | result: success | ip: 172.25.125.3
server   | 2024-08-21 22:11:35 INFO     action: receive_message | result: success | ip: 172.25.125.3 | msg: [CLIENT 1] Message N°5
client1  | 2024-08-21 22:11:35 INFO     action: receive_message | result: success | client_id: 1 | msg: [CLIENT 1] Message N°5
server   | 2024-08-21 22:11:35 INFO     action: accept_connections | result: in_progress
client1  | 2024-08-21 22:11:40 INFO     action: loop_finished | result: success | client_id: 1
client1 exited with code 0
```


<a id="parte-1-introduccion-a-docker"></a>
## Parte 1: Introducción a Docker
En esta primera parte del trabajo práctico se plantean una serie de ejercicios que sirven para introducir las herramientas básicas de Docker que se utilizarán a lo largo de la materia. El entendimiento de las mismas será crucial para el desarrollo de los próximos TPs.

<a id="ejercicio-1"></a>
### Ejercicio N°1:
Definir un script de bash `generar-compose.sh` que permita crear una definición de Docker Compose con una cantidad configurable de clientes.  El nombre de los containers deberá seguir el formato propuesto: client1, client2, client3, etc. 

El script deberá ubicarse en la raíz del proyecto y recibirá por parámetro el nombre del archivo de salida y la cantidad de clientes esperados:

`./generar-compose.sh docker-compose-dev.yaml 5`

Considerar que en el contenido del script pueden invocar un subscript de Go o Python:

```
#!/bin/bash
echo "Nombre del archivo de salida: $1"
echo "Cantidad de clientes: $2"
python3 mi-generador.py $1 $2
```

En el archivo de Docker Compose de salida se pueden definir volúmenes, variables de entorno y redes con libertad, pero recordar actualizar este script cuando se modifiquen tales definiciones en los sucesivos ejercicios.

#### Desarrollo realizado

Para este ejercicio se implementó la solución en dos componentes:

- Un script de bash `generar-compose.sh`, ubicado en la raíz del proyecto, que actúa como punto de entrada.
- Un script de Python `mi-generador.py`, también en la raíz, que se encarga de generar efectivamente el archivo de Docker Compose.

El uso de `generar-compose.sh` es:

```bash
./generar-compose.sh <nombre_archivo_salida> <cantidad_clientes>
```

Ejemplo de uso:

```bash
./generar-compose.sh docker-compose-dev.yaml 5
```

`generar-compose.sh` simplemente recibe los parámetros, muestra por pantalla el nombre del archivo de salida y la cantidad de clientes, y luego delega la lógica en `mi-generador.py`, pasándole esos mismos argumentos. 

`mi-generador.py` se encarga de:
- Crear los servicios `client1`, `client2`, ..., `clientN` según la cantidad indicada.
- Mantener la estructura base del compose (servicio `server`, redes, volúmenes, etc.).
- Sobrescribir el archivo de salida si ya existe, de modo que correr nuevamente el script regenere el compose acorde a la nueva cantidad de clientes.

Adicionalmente, se incorporó manejo explícito de dependencias entre el servidor y los clientes utilizando **healthchecks** de Docker:

- En `mi-generador.py` se definió un `healthcheck` para el servicio `server` que ejecuta el script `/healthcheck.sh` dentro del contenedor. Este script, ubicado en [server/healthcheck.sh](server/healthcheck.sh), lee el `SERVER_PORT` desde `config.ini` y usa `nc` para verificar que el puerto esté escuchando.
- Cada `clientN` se declara con `depends_on: server: condition: service_healthy`, de forma tal que Docker solo considere los clientes “listos” una vez que el healthcheck del servidor haya pasado.
- El `Dockerfile` del servidor instala `netcat-openbsd` y copia el código de `server/` en la imagen, permitiendo que el healthcheck use `nc` dentro del contenedor sin requerir herramientas adicionales en el host.

Con estos cambios, el `docker-compose` generado no solo crea dinámicamente la cantidad de clientes, sino que también garantiza que el servidor esté efectivamente aceptando conexiones antes de que los clientes comiencen a enviar mensajes.

<a id="ejercicio-2"></a>
### Ejercicio N°2:
Modificar el cliente y el servidor para lograr que realizar cambios en el archivo de configuración no requiera reconstruír las imágenes de Docker para que los mismos sean efectivos. La configuración a través del archivo correspondiente (`config.ini` y `config.yaml`, dependiendo de la aplicación) debe ser inyectada en el container y persistida por fuera de la imagen (hint: `docker volumes`).

#### Desarrollo realizado

Para este ejercicio se reutilizó el mismo flujo `generar-compose.sh` → `mi-generador.py`, agregando en `mi-generador.py` la lógica necesaria para inyectar los archivos de configuración en los contenedores mediante volúmenes.

En particular, el generador ahora:

- Define en el servicio del servidor un volumen que mapea el archivo de configuración local `server/config.ini` dentro del contenedor (por ejemplo, en `/config.ini`), de forma de poder modificar la configuración del servidor sin reconstruir la imagen.
- Define en cada cliente un volumen que mapea `client/config.yaml` dentro del contenedor (por ejemplo, en `/config.yaml`), permitiendo cambiar la configuración del cliente desde el host y reutilizar la misma imagen para todos los ejercicios.
 - Elimina variables de entorno hardcodeadas relacionadas con configuración (por ejemplo `LOGGING_LEVEL`, `CLI_LOG_LEVEL`), de modo que esos valores pasen a ser tomados desde los archivos de configuración montados, y no queden “fijos” en el `docker-compose` generado.

El uso del script se mantiene igual que en el Ejercicio 1:

```bash
./generar-compose.sh docker-compose-dev.yaml 5
```

La diferencia es que ahora el archivo `docker-compose-dev.yaml` generado ya incluye las secciones `volumes` y los mapeos necesarios para `config.ini` y `config.yaml`, cumpliendo con el requisito de que los cambios de configuración se apliquen solo modificando archivos en el host, sin necesidad de volver a hacer `docker build`.

Complementariamente, se actualizó el target `docker-compose-up` del `Makefile` para quitar el flag `--build` de `docker compose up`. De esta forma:

- La reconstrucción de imágenes queda explícitamente acotada al target `docker-image`.
- Al ejecutar `make docker-compose-up` se reutilizan las imágenes existentes y solo se levantan los contenedores, respetando los cambios de configuración montados por volumen sin forzar un rebuild innecesario.


<a id="ejercicio-3"></a>
### Ejercicio N°3:
Crear un script de bash `validar-echo-server.sh` que permita verificar el correcto funcionamiento del servidor utilizando el comando `netcat` para interactuar con el mismo. Dado que el servidor es un echo server, se debe enviar un mensaje al servidor y esperar recibir el mismo mensaje enviado.

En caso de que la validación sea exitosa imprimir: `action: test_echo_server | result: success`, de lo contrario imprimir:`action: test_echo_server | result: fail`.

El script deberá ubicarse en la raíz del proyecto. Netcat no debe ser instalado en la máquina _host_ y no se pueden exponer puertos del servidor para realizar la comunicación (hint: `docker network`). `

#### Desarrollo realizado

Para este ejercicio se implementó el script `validar-echo-server.sh` en la raíz del proyecto, utilizando un contenedor temporal con `busybox` para ejecutar `nc` (netcat) dentro de la misma red de Docker que el servidor, cumpliendo así con la restricción de no instalar netcat en el _host_ ni exponer puertos.

El uso típico es:

```bash
make docker-compose-up
./validar-echo-server.sh
```

El script:

- Asume que el servidor está accesible en el servicio `server` por el puerto `12345`, dentro de la red `tp0_testing_net` definida en el `docker-compose-dev.yaml`.
- Envía un mensaje de prueba (`"Mensaje de test"`) al servidor mediante:
	- `docker run -i --rm --network tp0_testing_net busybox nc -w 2 server 12345`
	- De este modo, la comunicación se hace enteramente dentro de la red de Docker, sin exponer puertos al exterior.
- Lee la respuesta, limpia caracteres de retorno de carro (`\r`) y compara texto enviado vs. recibido.
	- Si coinciden exactamente, imprime: `action: test_echo_server | result: success`.
	- En caso contrario, imprime: `action: test_echo_server | result: fail`.

De esta forma, `validar-echo-server.sh` permite verificar rápidamente desde el host el comportamiento de _echo_ del servidor ya desplegado en Docker, reutilizando la misma red del compose y sin dependencias extra en la máquina local.


<a id="ejercicio-4"></a>
### Ejercicio N°4:
Modificar servidor y cliente para que ambos sistemas terminen de forma _graceful_ al recibir la signal SIGTERM. Terminar la aplicación de forma _graceful_ implica que todos los _file descriptors_ (entre los que se encuentran archivos, sockets, threads y procesos) deben cerrarse correctamente antes que el thread de la aplicación principal muera. Loguear mensajes en el cierre de cada recurso (hint: Verificar que hace el flag `-t` utilizado en el comando `docker compose down`).

#### Desarrollo realizado

Para este ejercicio se implementó un mecanismo de apagado _graceful_ en **servidor** y **cliente** frente a `SIGTERM` (la señal que envía Docker al frenar containers). La idea general es:

- Señalizar a la aplicación que debe dejar de trabajar.
- Evitar quedar bloqueado indefinidamente esperando I/O.
- Cerrar sockets abiertos (tanto el socket de escucha como el socket del cliente), dejando el proceso en un estado consistente.
- Loguear el progreso del apagado para poder verificarlo por `docker compose logs`.

##### Servidor (Python)

La lógica está encapsulada en la clase `Server` y el loop de aceptación de conexiones. Los puntos relevantes son:

- **Handler de SIGTERM:** se registra `signal.signal(signal.SIGTERM, ...)` y al recibir la señal se loguea `action: graceful_shutdown | result: in_progress` y se setea el flag `_should_be_running = False`.
- **Salida del loop sin bloqueo (por qué hay timeout):**
	- `accept()` es una llamada **bloqueante**: si el servidor queda “idle” (no llegan clientes) se quedaría esperando indefinidamente una nueva conexión.
	- El handler de `SIGTERM` solo setea un flag (`_should_be_running = False`). Para que ese cambio tenga efecto, el server tiene que volver a ejecutar el `while` y evaluar la condición.
	- Por eso el socket de escucha se configura con `settimeout(...)` (por defecto 2s): así `accept()` deja de ser “espera infinita” y pasa a **despertar periódicamente** levantando `socket.timeout`.
	- Cada vez que vence el timeout, el servidor vuelve al loop, re-chequea `_should_be_running` y, si ya recibió `SIGTERM`, puede salir del `while` y ejecutar el cierre.

	En otras palabras: el timeout garantiza que si se mandó `SIGTERM` cuando no están entrando conexiones, el servidor no queda colgado esperando un `accept()` que nunca retorna; en cambio, como máximo en ~`accept_timeout` segundos vuelve al loop y confirma el apagado.
- **Cierre de recursos:**
	- El socket del cliente (si existe) se cierra en un único lugar (`__clear()`), intentando primero `shutdown(SHUT_RDWR)` y luego `close()`, y limpiando la referencia (`self.client = None`).
	- El socket de escucha se cierra en `__stop()` con `self._server_socket.close()`.
- **Manejo de errores en comunicación:** el `recv/send` de cada conexión está envuelto en `try/except OSError` y ante error se loguea `action: receive_message | result: fail | error: ...`, garantizando igualmente el cleanup en `finally`.

##### Cliente (Go)

La lógica está en el loop del cliente y un listener de señales:

- **Listener de SIGTERM (goroutine + channels):**
	- Se crea un channel `sigs := make(chan os.Signal, 1)`. El buffer de tamaño 1 evita que se pierda la señal si llega cuando todavía nadie está recibiendo.
	- `signal.Notify(sigs, syscall.SIGTERM)` le dice al runtime: “cuando llegue `SIGTERM`, en vez de matar el proceso inmediatamente, entregá esa señal por el channel `sigs`”.
	- Se lanza una goroutine que hace un receive bloqueante: `<-sigs`. Esa goroutine queda esperando sin consumir CPU.
	- Cuando Docker envía `SIGTERM`, el runtime escribe un valor en el channel, el receive se desbloquea, y ahí se:
		- Loguea `action: graceful_shutdown | result: in_progress`.
		- Cambia el flag `should_be_running = false`.
	- El loop principal del cliente evalúa ese flag en la condición del `for`, por lo que deja de iterar y no crea nuevas conexiones.

	Este patrón separa responsabilidades: la goroutine solo “traduce” la señal a un cambio de estado, y el loop principal aplica el apagado de forma ordenada.
- **Cierre de sockets:** el cliente abre una conexión TCP por iteración y la cierra explícitamente al terminar de leer la respuesta (`c.conn.Close()`), evitando acumular descriptores.
- **Salida controlada del loop:** al bajar el flag `should_be_running`, el `for` deja de iterar y no se crean nuevas conexiones.

##### Cómo verificar el apagado

1. Levantar el entorno: `make docker-compose-up`.
2. Ver logs: `make docker-compose-logs`.
3. Abrir otra terminal y ejecutar: `make docker-compose-down`.
4. Verificar en logs:
	- Servidor: `action: graceful_shutdown | result: in_progress` y luego uno o más `action: graceful_shutdown | result: success`.
	- Cliente: `action: graceful_shutdown | result: in_progress` y que deja de generar nuevas conexiones/mensajes.

<a id="parte-2-repaso-de-comunicaciones"></a>
## Parte 2: Repaso de Comunicaciones

Las secciones de repaso del trabajo práctico plantean un caso de uso denominado **Lotería Nacional**. Para la resolución de las mismas deberá utilizarse como base el código fuente provisto en la primera parte, con las modificaciones agregadas en el ejercicio 4.

<a id="ejercicio-5"></a>
### Ejercicio N°5:
Modificar la lógica de negocio tanto de los clientes como del servidor para nuestro nuevo caso de uso.

#### Cliente
Emulará a una _agencia de quiniela_ que participa del proyecto. Existen 5 agencias. Deberán recibir como variables de entorno los campos que representan la apuesta de una persona: nombre, apellido, DNI, nacimiento, numero apostado (en adelante 'número'). Ej.: `NOMBRE=Santiago Lionel`, `APELLIDO=Lorca`, `DOCUMENTO=30904465`, `NACIMIENTO=1999-03-17` y `NUMERO=7574` respectivamente.

Los campos deben enviarse al servidor para dejar registro de la apuesta. Al recibir la confirmación del servidor se debe imprimir por log: `action: apuesta_enviada | result: success | dni: ${DNI} | numero: ${NUMERO}`.



#### Servidor
Emulará a la _central de Lotería Nacional_. Deberá recibir los campos de la cada apuesta desde los clientes y almacenar la información mediante la función `store_bet(...)` para control futuro de ganadores. La función `store_bet(...)` es provista por la cátedra y no podrá ser modificada por el alumno.
Al persistir se debe imprimir por log: `action: apuesta_almacenada | result: success | dni: ${DNI} | numero: ${NUMERO}`.

#### Comunicación:
Se deberá implementar un módulo de comunicación entre el cliente y el servidor donde se maneje el envío y la recepción de los paquetes, el cual se espera que contemple:
* Definición de un protocolo para el envío de los mensajes.
* Serialización de los datos.
* Correcta separación de responsabilidades entre modelo de dominio y capa de comunicación.
* Correcto empleo de sockets, incluyendo manejo de errores y evitando los fenómenos conocidos como [_short read y short write_](https://cs61.seas.harvard.edu/site/2018/FileDescriptors/).

#### Desarrollo realizado

En este ejercicio el cambio principal no está en “mandar un string” como en el echo server, sino en definir un **protocolo** para transportar una **apuesta** (modelo de dominio) entre dos entidades (agencia ↔ central) de forma determinística y robusta.

La solución se estructura en dos capas bien separadas:

- **Modelo de dominio (Bet):** representa una apuesta con sus campos tipados.
- **Capa de comunicación (Protocol):** define cómo se serializa/deserializa esa apuesta sobre TCP.

##### Modelado

Se definió la entidad **Bet** en ambos componentes, respetando el mismo set de atributos:

- `agency`: id de la agencia que envía la apuesta.
- `first_name`, `last_name`: nombre y apellido.
- `document`: DNI.
- `birthdate`: fecha de nacimiento en formato `YYYY-MM-DD`.
- `number`: número apostado.

En el servidor, el modelo vive en `server/model/bet.py` (incluye además la persistencia vía `store_bets(...)`). En el cliente, el DTO equivalente está en `client/common/model/bet.go`.

##### Protocolo de comunicación

Se implementó un protocolo **binario** simple y explícito (Big Endian) para evitar ambigüedades de parsing y depender lo menos posible de formatos de texto.

La comunicación se modela como una secuencia de:

1. **Cliente → Servidor:** `OpCode` + payload.
2. **Servidor → Cliente:** ACK de registro.

**OpCodes**

- El primer byte del mensaje es un `OpCode` (opcode) que indica qué operación se quiere ejecutar (no confundir con el campo `action:` de los logs).
- Para Ej5 se definió `REGISTER_SINGLE_BET = 0x01`.

**Formato del mensaje `REGISTER_SINGLE_BET`**

El cliente envía, en este orden:

1. `opCode`: `uint8` (1 byte)
2. `agency`: `uint32` (4 bytes)
3. `first_name`: `uint8 len` + `len` bytes UTF-8
4. `last_name`: `uint8 len` + `len` bytes UTF-8
5. `document`: `uint32` (4 bytes)
6. `birthdate`: `uint8 len` + `len` bytes UTF-8
7. `number`: `uint32` (4 bytes)

Este diseño hace que el stream sea auto-delimitado: los strings incluyen su longitud, y los enteros tienen tamaño fijo.

**Respuesta (ACK)**

- El servidor responde con 1 byte.
- `0x00` significa “apuesta registrada OK”.
- Cualquier valor distinto de `0x00` se interpreta como error.

##### Implementación del protocolo

- **Cliente:** `client/common/protocol/protocol.go`
	- Serializa con `encoding/binary` en Big Endian.
	- Para strings escribe `uint8(len)` + bytes.
	- Valida el ACK con `ReadBetRegistered()`.
	- Se agregaron tests unitarios del layout del paquete en `client/common/protocol/protocol_test.go` (verifica orden y tamaños de campos).

- **Servidor:** `server/common/protocol.py`
	- Interpreta el `opCode` (1 byte) y luego consume el payload.
	- Implementa `_read_exactly(n)` para evitar **short reads**: si `recv()` retorna menos bytes de los esperados, sigue leyendo hasta completar o detectar EOF.
	- Para strings lee primero 1 byte de longitud y luego exactamente esa cantidad de bytes.
	- Envía el ACK con `sendall` para evitar **short writes**.

##### Tests unitarios

A partir de este ejercicio se agregaron **tests unitarios** para validar el protocolo y el modelado sin depender de levantar Docker Compose.

- **Cliente (Go):**
	- Los tests del protocolo viven en `client/common/protocol/protocol_test.go`.
	- Validan el **layout** del mensaje: orden de campos, tamaños (`uint8`/`uint32`) y encoding Big Endian.
	- Ejecución: `make test-client`.

- **Servidor (Python):**
	- Los tests viven en `server/tests/` (por ejemplo `test_protocol.py`, `test_client_handler.py`, `test_bet.py`).
	- Ejecución: `make test-server`.
	- El target crea un `venv`, instala `pytest` y corre los tests con `PYTHONPATH` configurado para que los imports del servidor funcionen.

<a id="ejercicio-6"></a>
### Ejercicio N°6:
Modificar los clientes para que envíen varias apuestas a la vez (modalidad conocida como procesamiento por _chunks_ o _batchs_). 
Los _batchs_ permiten que el cliente registre varias apuestas en una misma consulta, acortando tiempos de transmisión y procesamiento.

La información de cada agencia será simulada por la ingesta de su archivo numerado correspondiente, provisto por la cátedra dentro de `.data/datasets.zip`.
Los archivos deberán ser inyectados en los containers correspondientes y persistido por fuera de la imagen (hint: `docker volumes`), manteniendo la convencion de que el cliente N utilizara el archivo de apuestas `.data/agency-{N}.csv` .

En el servidor, si todas las apuestas del *batch* fueron procesadas correctamente, imprimir por log: `action: apuesta_recibida | result: success | cantidad: ${CANTIDAD_DE_APUESTAS}`. En caso de detectar un error con alguna de las apuestas, debe responder con un código de error a elección e imprimir: `action: apuesta_recibida | result: fail | cantidad: ${CANTIDAD_DE_APUESTAS}`.

La cantidad máxima de apuestas dentro de cada _batch_ debe ser configurable desde config.yaml. Respetar la clave `batch: maxAmount`, pero modificar el valor por defecto de modo tal que los paquetes no excedan los 8kB. 

Por su parte, el servidor deberá responder con éxito solamente si todas las apuestas del _batch_ fueron procesadas correctamente.

#### Desarrollo realizado

En este ejercicio se introdujo el concepto de **batches** para optimizar la transmisión de apuestas, permitiendo enviar múltiples apuestas en una sola consulta TCP, reduciendo la latencia y mejorando la eficiencia de red.

##### Limitación de tamaño de paquetes

Se impuso una limitación máxima de **8 kB** por paquete para evitar fragmentación excesiva y optimizar el uso de buffers. Esta restricción afecta directamente la cantidad máxima de apuestas por batch, ya que cada apuesta tiene un tamaño variable debido a los campos de texto (nombres y fecha de nacimiento).

- **Campos fijos por apuesta:** `agency` (4 bytes, uint32), `document` (4 bytes, uint32), `number` (4 bytes, uint32) → 12 bytes total.
- **Campos dinámicos:** `first_name`, `last_name`, `birthdate` (cada uno: 1 byte para longitud + N bytes UTF-8).
- **Estimación conservadora:** Asumiendo nombres típicos (ej. 10 caracteres cada uno) y fecha (10 caracteres), los strings suman ~33 bytes (11 + 11 + 11).
- **Tamaño total por apuesta aproximado:** 12 + 33 = 45 bytes.
- **Máxima cantidad de apuestas por batch:** 8192 bytes / 45 bytes ≈ 182 apuestas. Este valor se configuró como default en `config.yaml` bajo `batch.maxAmount`, ajustable según necesidades.

##### Nuevos OpCodes

Se agregó el OpCode `REGISTER_BATCH_OF_BETS = 0x02` para distinguir el envío de batches del registro individual.

**Formato del mensaje `REGISTER_BATCH_OF_BETS`:**

1. `opCode`: `uint8` (1 byte, valor 0x02)
2. `batch_size`: `uint32` (4 bytes, cantidad de apuestas en el batch)
3. Repetir `batch_size` veces el payload de una apuesta individual (sin opCode):
   - `agency`: `uint32`
   - `first_name`: `uint8 len` + `len` bytes UTF-8
   - `last_name`: `uint8 len` + `len` bytes UTF-8
   - `document`: `uint32`
   - `birthdate`: `uint8 len` + `len` bytes UTF-8
   - `number`: `uint32`

**Respuesta (ACK):**

- `0x00`: Todas las apuestas del batch procesadas correctamente.
- `0x01`: Error en al menos una apuesta (el batch se rechaza por completo).

##### Implementación

- **Cliente (Go):** Se modificó para leer archivos CSV (`.data/agency-{N}.csv`) usando un reader CSV. Las apuestas se agrupan en batches según `batch.maxAmount`, serializando y enviando cada batch. Se agregó logging para `action: batch_enviado | result: success | cantidad: ${N}`.
- **Servidor (Python):** Se extendió el protocolo para leer `batch_size` y procesar múltiples apuestas. Si `store_bets(bets)` falla para alguna, se responde con error y se loguea `result: fail`. De lo contrario, `result: success`.
- **Configuración:** `config.yaml` incluye `batch.maxAmount` con default calculado para no exceder 8kB. Los archivos CSV se montan vía volúmenes en Docker Compose.
- **Tests:** Se agregaron tests unitarios para validar el parsing de batches y límites de tamaño.

<a id="ejercicio-7"></a>
### Ejercicio N°7:

Modificar los clientes para que notifiquen al servidor al finalizar con el envío de todas las apuestas y así proceder con el sorteo.
Inmediatamente después de la notificacion, los clientes consultarán la lista de ganadores del sorteo correspondientes a su agencia.
Una vez el cliente obtenga los resultados, deberá imprimir por log: `action: consulta_ganadores | result: success | cant_ganadores: ${CANT}`.

El servidor deberá esperar la notificación de las 5 agencias para considerar que se realizó el sorteo e imprimir por log: `action: sorteo | result: success`.
Luego de este evento, podrá verificar cada apuesta con las funciones `load_bets(...)` y `has_won(...)` y retornar los DNI de los ganadores de la agencia en cuestión. Antes del sorteo no se podrán responder consultas por la lista de ganadores con información parcial.

Las funciones `load_bets(...)` y `has_won(...)` son provistas por la cátedra y no podrán ser modificadas por el alumno.

No es correcto realizar un broadcast de todos los ganadores hacia todas las agencias, se espera que se informen los DNIs ganadores que correspondan a cada una de ellas.

<a id="parte-3-repaso-de-concurrencia"></a>
## Parte 3: Repaso de Concurrencia
En este ejercicio es importante considerar los mecanismos de sincronización a utilizar para el correcto funcionamiento de la persistencia.

<a id="ejercicio-8"></a>
### Ejercicio N°8:

Modificar el servidor para que permita aceptar conexiones y procesar mensajes en paralelo. En caso de que el alumno implemente el servidor en Python utilizando _multithreading_,  deberán tenerse en cuenta las [limitaciones propias del lenguaje](https://wiki.python.org/moin/GlobalInterpreterLock).

<a id="condiciones-de-entrega"></a>
## Condiciones de Entrega
Se espera que los alumnos realicen un _fork_ del presente repositorio para el desarrollo de los ejercicios y que aprovechen el esqueleto provisto tanto (o tan poco) como consideren necesario.

Cada ejercicio deberá resolverse en una rama independiente con nombres siguiendo el formato `ej${Nro de ejercicio}`. Se permite agregar commits en cualquier órden, así como crear una rama a partir de otra, pero al momento de la entrega deberán existir 8 ramas llamadas: ej1, ej2, ..., ej7, ej8.
 (hint: verificar listado de ramas y últimos commits con `git ls-remote`)

Se espera que se redacte una sección del README en donde se indique cómo ejecutar cada ejercicio y se detallen los aspectos más importantes de la solución provista, como ser el protocolo de comunicación implementado (Parte 2) y los mecanismos de sincronización utilizados (Parte 3).

Se proveen [pruebas automáticas](https://github.com/7574-sistemas-distribuidos/tp0-tests) de caja negra. Se exige que la resolución de los ejercicios pase tales pruebas, o en su defecto que las discrepancias sean justificadas y discutidas con los docentes antes del día de la entrega. 

El incumplimiento de las pruebas es condición de desaprobación, pero su cumplimiento no es suficiente para la aprobación.  Se pide a los alumnos leer atentamente y **tener en cuenta** los criterios de corrección informados  [en el campus](https://campusgrado.fi.uba.ar/mod/page/view.php?id=73393).
Respetar el formato y contenido las entradas de logs descritas en los ejercicios, pues son las que se chequean en cada uno de los tests.
