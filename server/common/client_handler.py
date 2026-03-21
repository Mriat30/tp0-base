from .protocol import OpCode
from model.bet import store_bets
import logging

class ClientHandler:
    def __init__(self, protocol, lottery, logger=None):
        self._protocol = protocol
        self._should_be_running = False
        self._logger = logger or logging.getLogger(__name__)
        self._lottery = lottery

    def start(self):
        """
        Read message from a specific client socket

        If a problem arises in the communication with the client, the
        client socket will also be closed
        """
        self._should_be_running = True
        try:
            addr = self._protocol._socket.getpeername()
            
            action = self._protocol.read_action()
            self._protocol.read_client_id()
            self._logger.debug(f"action: handshake | result: success | ip: {addr[0]} | client_id: {self._protocol._client_id}")
            
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
        if action == OpCode.REGISTER_SINGLE_BET:
            bet = self._protocol.read_bet()
            store_bets([bet])
            self._protocol.send_bet_registered()
            self._logger.info(f'action: apuesta_recibida | result: success | ip: {addr[0]} | dni: {bet.document}')
        elif action == OpCode.REGISTER_BATCH_OF_BETS:
            bets = self._protocol.read_batch_of_bets()
            store_bets(bets)
            self._protocol.send_bet_registered()
            self._logger.info(f'action: apuesta_recibida | result: success | ip: {addr[0]} | cantidad: {len(bets)}')
        elif action == OpCode.WAITING_FOR_WINNERS:
            self._lottery.notify_done(self._protocol._client_id, self._protocol)
            self._logger.info(f"action: waiting_for_winners | result: success | ip: {addr[0]} | client_id: {self._protocol._client_id}")
            self._protocol = None
            self._should_be_running = False
        else:
            self._logger.error(f"action: receive_message | result: fail | error: unknown_action")

    def stop(self):
        self._should_be_running = False
        if self._protocol:
            self._protocol.close()