import socket
from common.utils import ActionType
from model.bet import Bet

class ServerProtocol:
    _CHAR_SIZE = 1
    _INT_SIZE = 4

    def __init__(self, socket):
        self._socket = socket

    def read_action(self):
        action = self._socket.recv(self._CHAR_SIZE)
        return ActionType.from_bytes(action)

    def read_bet(self):
        agency_raw = self._read_exactly(self._INT_SIZE)
        agency = str(int.from_bytes(agency_raw, byteorder='big'))

        first_name = self._read_string()
        last_name = self._read_string()
        document = self._read_string()
        birthdate = self._read_string()
        number = self._read_string()

        return Bet(agency, first_name, last_name, document, birthdate, number)

    def _read_string(self):
        raw_len = self._socket.recv(self._CHAR_SIZE)
        if not raw_len: return ""
        length = int.from_bytes(raw_len, byteorder='big')
        return self._read_exactly(length).decode('utf-8')

    def _read_exactly(self, n):
        data = b''
        while len(data) < n:
            packet = self._socket.recv(n - len(data))
            if not packet: raise EOFError("Socket cerrado")
            data += packet
        return data