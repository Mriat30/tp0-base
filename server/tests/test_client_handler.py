import unittest
from unittest.mock import MagicMock, patch
from common.client_handler import ClientHandler
from common.protocol import ActionType
from model.bet import Bet, STORAGE_FILEPATH, store_bets
import os

class TestClientHandler(unittest.TestCase):

    def tearDown(self):
        if os.path.exists(STORAGE_FILEPATH):
            os.remove(STORAGE_FILEPATH)

    @patch('common.client_handler.store_bets')
    def test_handle_single_bet_success(self, mock_store):
        mock_socket = MagicMock()
        mock_socket.getpeername.return_value = ('127.0.0.1', 12345)
        expected_bet = Bet("1", "Juan", "Perez", "12345678", "1990-01-01", "7574")
        handler = ClientHandler(mock_socket)
        handler._protocol.read_action = MagicMock(side_effect=[
            ActionType.REGISTER_SINGLE_BET, 
            EOFError
        ])
        handler._protocol.read_bet = MagicMock(return_value=expected_bet)
        handler._protocol.send_bet_registered = MagicMock()

        handler.start()

        mock_store.assert_called_once_with([expected_bet])
        handler._protocol.send_bet_registered.assert_called_once()
        mock_socket.close.assert_called_once()

    @patch('common.client_handler.store_bets')
    def test_handle_batch_fails_if_storage_fails(self, mock_store):
        # 1. Preparación de Mocks
        mock_socket = MagicMock()
        mock_socket.getpeername.return_value = ('127.0.0.1', 12345)
        mock_log = MagicMock() 
        expected_bets = [
            Bet(1, "Juan", "Perez", 12345678, "1990-01-01", 7574),
            Bet(2, "Maria", "Gomez", 87654321, "1995-05-05", 1234)
        ]
        mock_store.side_effect = Exception("Storage error")
        handler = ClientHandler(mock_socket, logger=mock_log)
        
        handler._protocol.read_action = MagicMock(side_effect=[
            ActionType.REGISTER_BATCH_OF_BETS,
            EOFError
        ])
        handler._protocol.read_batch_of_bets = MagicMock(return_value=expected_bets)
        handler._protocol.send_bet_registered = MagicMock()

        handler.start()

        mock_store.assert_called_once_with(expected_bets)
        handler._protocol.send_bet_registered.assert_not_called()
        
        error_logged = any("result: fail" in str(call) for call in mock_log.mock_calls)
        self.assertTrue(error_logged)
        mock_socket.close.assert_called()

if __name__ == '__main__':
    unittest.main()