import socket
from common.utils import OpCode
from model.bet import Bet
from model.lottery_winner import LotteryWinner
import logging

class ServerProtocol:
    _CHAR_SIZE = 1
    _INT_SIZE = 4

    def __init__(self, socket, logger=None):
        self._socket = socket
        self._client_id = None
        self._logger = logger or logging.getLogger(__name__)

    def read_client_id(self):
        client_id = self._read_int()
        self._client_id = client_id
        return client_id
    
    def set_client_id(self, client_id):
        self._client_id = client_id

    def read_action(self):
        action = self._socket.recv(self._CHAR_SIZE)
        if not action: raise EOFError("Socket cerrado por el cliente")
        return OpCode.from_bytes(action)

    def read_bet(self):
        first_name = self._read_string()
        last_name = self._read_string()
        document = self._read_int()
        birthdate = self._read_string()
        number = self._read_int()

        return Bet(self._client_id, first_name, last_name, document, birthdate, number)
    
    def read_batch_of_bets(self):
        batch_size = self._read_int()
        bets = []
        for _ in range(batch_size):
            bets.append(self.read_bet())
        return bets

    def send_bet_registered(self):
        try:
            self._socket.sendall(OpCode.BET_REGISTERED.value.to_bytes(self._CHAR_SIZE, byteorder='big'))
        except OSError:
            raise EOFError("Socket cerrado por el cliente")

    def send_winners(self, list_of_winners: list[LotteryWinner]):
        self._socket.sendall(OpCode.WINNERS.value.to_bytes(self._CHAR_SIZE, byteorder='big'))
        winners_docs = [w.document for w in list_of_winners]
        winners_str = ",".join(winners_docs)
        winners_bytes = winners_str.encode('utf-8')
        self._socket.sendall(len(winners_bytes).to_bytes(self._INT_SIZE, byteorder='big'))
        self._socket.sendall(winners_bytes)

    def _read_int(self):
        raw = self._read_exactly(self._INT_SIZE)
        return int.from_bytes(raw, byteorder='big')

    def _read_string(self):
        raw_len = self._socket.recv(self._CHAR_SIZE)
        if not raw_len: raise EOFError("Socket cerrado por el cliente")
        length = int.from_bytes(raw_len, byteorder='big')
        return self._read_exactly(length).decode('utf-8')

    def _read_exactly(self, n):
        data = b''
        while len(data) < n:
            packet = self._socket.recv(n - len(data))
            if not packet: raise EOFError("Socket cerrado por el cliente")
            data += packet
        return data

    def close(self):
        if self._socket:
            try:
                self._socket.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            
            self._socket.close()
            self._socket = None 
            self._logger.debug("action: socket_closed | result: success")