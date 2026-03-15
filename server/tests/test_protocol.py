from common.protocol import ServerProtocol
from common.utils import ActionType
import unittest
from unittest.mock import MagicMock

class TestProtocol(unittest.TestCase):
   def test_protocol_read_action_success(self):
        socket = MagicMock()
        socket.recv.return_value = b'\x01' 
        
        protocol = ServerProtocol(socket)
        
        action = protocol.read_action()
        
        self.assertEqual(action, ActionType.REGISTER_SINGLE_BET)

if __name__ == '__main__':
    unittest.main()