from .protocol import ServerProtocol
from .protocol import ActionType
from model.bet import store_bets
import logging
import socket

class ClientHandler:
    def __init__(self, socket):
        self._socket = socket
        self._protocol = ServerProtocol(self._socket)
        self._should_be_running = False

    def start(self):
        """
        Read message from a specific client socket and closes the socket

        If a problem arises in the communication with the client, the
        client socket will also be closed
        """
        self._should_be_running = True
        try:
            addr = self._socket.getpeername()
            
            while self._should_be_running:
                action = self._protocol.read_action()
                
                if action == ActionType.REGISTER_SINGLE_BET:
                    bet = self._protocol.read_bet()
                    store_bets([bet])
                    self._protocol.send_bet_registered()
                    logging.info(f'action: apuesta_almacenada | result: success | ip: {addr[0]} | dni: {bet.document}')
        except EOFError:
            logging.info(f"action: client_disconnection | result: success | ip: {addr[0]}")

        except OSError as e:
            logging.error(f"action: receive_message | result: fail | error: {e}")
        finally:
            self.stop()

    def stop(self):
        self._should_be_running = False
        if self._socket:
            try:
                self._socket.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            
            self._socket.close()
            self._socket = None 
            logging.debug("action: socket_closed | result: success")