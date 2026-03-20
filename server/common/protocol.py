import socket
from common.utils import OpCode
from model.bet import Bet

class ServerProtocol:
    _CHAR_SIZE = 1
    _INT_SIZE = 4

    def __init__(self, socket):
        self._socket = socket

    def read_client_id(self):
        client_id = self._read_int()
        return client_id

    def read_action(self):
        action = self._socket.recv(self._CHAR_SIZE)
        if not action: raise EOFError("Socket cerrado por el cliente")
        return OpCode.from_bytes(action)

    def read_bet(self):
        agency = self._read_int()
        first_name = self._read_string()
        last_name = self._read_string()
        document = self._read_int()
        birthdate = self._read_string()
        number = self._read_int()

        return Bet(agency, first_name, last_name, document, birthdate, number)
    
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