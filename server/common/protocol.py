import socket
from common.utils import ActionType

class ServerProtocol:
    _SIZE_ACTION_IN_BYTES = 1

    def __init__(self, socket):
        self.socket = socket

    def read_action(self):
        action = self.socket.recv(self._SIZE_ACTION_IN_BYTES)
        return ActionType.from_bytes(action)