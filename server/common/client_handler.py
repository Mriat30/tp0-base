from .protocol import ServerProtocol
from .protocol import ActionType
from model.bet import store_bets
import logging
import socket

class ClientHandler:
    def __init__(self, socket, logger=None):
        self._socket = socket
        self._protocol = ServerProtocol(self._socket)
        self._should_be_running = False
        self._logger = logger or logging.getLogger(__name__)

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
                self._process_action(action, addr)

        except EOFError:
            self._logger.info(f"action: client_disconnection | result: success | ip: {addr[0]}")
        except OSError as e:
            self._logger.error(f"action: receive_message | result: fail | error: {e}")
        except Exception as e:
            self._logger.error(f"action: receive_message | result: fail | error: {e}")
        finally:
            self.stop()

    def _process_action(self, action, addr):
        if action == ActionType.REGISTER_SINGLE_BET:
            bet = self._protocol.read_bet()
            store_bets([bet])
            self._protocol.send_bet_registered()
            self._logger.info(f'action: apuesta_almacenada | result: success | ip: {addr[0]} | dni: {bet.document}')
        elif action == ActionType.REGISTER_BATCH_OF_BETS:
            bets = self._protocol.read_batch_of_bets()
            store_bets(bets)
            self._protocol.send_bet_registered()
            self._logger.info(f'action: batch_de_apuestas_almacenado | result: success | ip: {addr[0]} | cantidad: {len(bets)}')
        else:
            self._logger.error(f"action: receive_message | result: fail | error: unknown_action")

    def stop(self):
        self._should_be_running = False
        if self._socket:
            try:
                self._socket.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            
            self._socket.close()
            self._socket = None 
            self._logger.debug("action: socket_closed | result: success")