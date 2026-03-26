import socket
import logging
import signal


class Server:

    _DEFAULT_ACCEPT_TIMEOUT = 2.0

    def __init__(self, port, listen_backlog, accept_timeout = None):
        # Initialize server socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)
        if accept_timeout is None:
            accept_timeout = self._DEFAULT_ACCEPT_TIMEOUT
        self._server_socket.settimeout(accept_timeout)
        self._should_be_running = False
        self.client = None
        signal.signal(signal.SIGTERM, self.__handle_sigterm)


    def run(self):
        """
        Dummy Server loop

        Server that accept a new connections and establishes a
        communication with a client. After client with communucation
        finishes, servers starts to accept new connections again
        """

        self._should_be_running = True
        while self._should_be_running:
            self.client = self.__accept_new_connection()
            if self.client is not None:
                self.__handle_client_connection()
        logging.info("action: graceful_shutdown | result: success")
        self.__stop()

    def __handle_client_connection(self):
        """
        Read message from a specific client socket and closes the socket

        If a problem arises in the communication with the client, the
        client socket will also be closed
        """
        client = self.client
        if client is None:
            return

        try:
            # TODO: Modify the receive to avoid short-reads
            msg = client.recv(1024).rstrip().decode('utf-8')
            addr = client.getpeername()
            logging.info(f'action: receive_message | result: success | ip: {addr[0]} | msg: {msg}')
            # TODO: Modify the send to avoid short-writes
            client.send("{}\n".format(msg).encode('utf-8'))
        except OSError as e:
            logging.error(f"action: receive_message | result: fail | error: {e}")
        finally:
            self.__clear()

    def __accept_new_connection(self):
        """
        Accept new connections

        Function blocks until a connection to a client is made.
        Then connection created is printed and returned
        """

        # Connection arrived
        try:
            logging.info('action: accept_connections | result: in_progress')
            c, addr = self._server_socket.accept()
            logging.info(f'action: accept_connections | result: success | ip: {addr[0]}')
            return c
        except socket.timeout:
            return None

    def __handle_sigterm(self, signum, frame):
        logging.info("action: graceful_shutdown | result: in_progress")
        self._should_be_running = False
    
    def __stop(self):
        logging.info("action: graceful_shutdown | result: in_progress")
        self.__clear()
        self._server_socket.close()
        logging.info("action: graceful_shutdown | result: success")

    def __clear(self):
        client = self.client
        if client is None:
            return
        try:
            client.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        finally:
            client.close()
            self.client = None