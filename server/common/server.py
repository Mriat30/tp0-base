import socket
import logging
import signal
from common.client_handler import ClientHandler
from common.lottery import Lottery
from common.protocol import ServerProtocol
import threading

class Server:

    _DEFAULT_ACCEPT_TIMEOUT = 2.0

    def __init__(self, port, listen_backlog, n_clients, accept_timeout = None):
        # Initialize server socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)
        if accept_timeout is None:
            accept_timeout = self._DEFAULT_ACCEPT_TIMEOUT
        self._server_socket.settimeout(accept_timeout)
        self._should_be_running = False
        self._lottery = Lottery(n_clients, logging.getLogger(__name__))
        self._clients = []
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
            self.__reaper()
            client_socket = self.__accept_new_connection()
            if client_socket:
                protocol = ServerProtocol(client_socket, logging.getLogger(__name__))
                handler = ClientHandler(protocol, self._lottery, logging.getLogger(__name__))
                thread = threading.Thread(target=handler.start)
                self.client.append((thread,handler))
                thread.start()

        logging.info("action: graceful_shutdown | result: success")
        self.__stop()
        
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
        for thread, handler in self._clients:
            handler.stop()

        for thread, handler in self._clients:
            thread.join(timeout=5.0)
            if thread.is_alive():
                logging.warning("action: graceful_shutdown | result: timeout")

        self._server_socket.close()
        logging.info("action: graceful_shutdown | result: success")

    def __reaper(self):
        alive = []
        for thread, handler in self._threads:
            if thread.is_alive():
                alive.append((thread, handler))
            else:
                thread.join()
                logging.debug("action: thread_reaped | result: success")
        self._clients = alive