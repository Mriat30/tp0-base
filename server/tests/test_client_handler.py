import unittest
from unittest.mock import MagicMock, patch
from common.client_handler import ClientHandler
from common.protocol import ActionType
from model.bet import Bet, STORAGE_FILEPATH, store_bets
import os

class TestClientHandler(unittest.TestCase):

    def setUp(self):
        self.mock_socket = MagicMock()
        self.mock_socket.getpeername.return_value = ('127.0.0.1', 12345)
        self.handler = ClientHandler(self.mock_socket)

    def tearDown(self):
        if os.path.exists(STORAGE_FILEPATH):
            os.remove(STORAGE_FILEPATH)

    @patch('common.client_handler.store_bets')
    def test_handle_single_bet_success(self, mock_store):
        expected_bet = Bet("1", "Juan", "Perez", "12345678", "1990-01-01", "7574")
        self.handler._protocol.read_action = MagicMock(side_effect=[
            ActionType.REGISTER_SINGLE_BET, 
            EOFError
        ])
        self.handler._protocol.read_bet = MagicMock(return_value=expected_bet)
        self.handler._protocol.send_bet_registered = MagicMock()

        self.handler.start()

        mock_store.assert_called_once_with([expected_bet])
        self.handler._protocol.send_bet_registered.assert_called_once()
        self.mock_socket.close.assert_called_once()

    @patch('common.client_handler.store_bets')
    def test_handle_batch_fails_if_storage_fails(self, mock_store):
        mock_log = MagicMock() 
        expected_bets = [
            Bet(1, "Juan", "Perez", 12345678, "1990-01-01", 7574),
            Bet(2, "Maria", "Gomez", 87654321, "1995-05-05", 1234)
        ]
        mock_store.side_effect = Exception("Storage error")
        self.handler = ClientHandler(self.mock_socket, logger=mock_log)
        
        self.handler._protocol.read_action = MagicMock(side_effect=[
            ActionType.REGISTER_BATCH_OF_BETS,
            EOFError
        ])
        self.handler._protocol.read_batch_of_bets = MagicMock(return_value=expected_bets)
        self.handler._protocol.send_bet_registered = MagicMock()

        self.handler.start()

        mock_store.assert_called_once_with(expected_bets)
        self.handler._protocol.send_bet_registered.assert_not_called()
        
        error_logged = any("result: fail" in str(call) for call in mock_log.mock_calls)
        self.assertTrue(error_logged)
        self.mock_socket.close.assert_called()

if __name__ == '__main__':
    unittest.main()