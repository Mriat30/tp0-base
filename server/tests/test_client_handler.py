import unittest
import os
from unittest.mock import MagicMock, patch
from common.client_handler import ClientHandler
from common.protocol import ActionType
from model.bet import Bet, STORAGE_FILEPATH

class TestClientHandler(unittest.TestCase):
    def setUp(self):
        self.mock_socket = MagicMock()
        self.mock_socket.getpeername.return_value = ('127.0.0.1', 12345)
        self.mock_log = MagicMock()
        self.handler = ClientHandler(self.mock_socket, logger=self.mock_log)
        self.proto = self.handler._protocol
        self.proto.send_bet_registered = MagicMock()

    def tearDown(self):
        if os.path.exists(STORAGE_FILEPATH):
            os.remove(STORAGE_FILEPATH)

    def _prepare_proto(self, action, return_val, is_batch=False):
        self.proto.read_action = MagicMock(side_effect=[action, EOFError])
        if is_batch:
            self.proto.read_batch_of_bets = MagicMock(return_value=return_val)
        else:
            self.proto.read_bet = MagicMock(return_value=return_val)

    @patch('common.client_handler.store_bets')
    def test_handle_single_bet_success(self, mock_store):
        bet = Bet("1", "Juan", "Perez", "12345678", "1990-01-01", "7574")
        self._prepare_proto(ActionType.REGISTER_SINGLE_BET, bet)

        self.handler.start()

        mock_store.assert_called_once_with([bet])
        self.proto.send_bet_registered.assert_called_once()
        self.mock_socket.close.assert_called()

    @patch('common.client_handler.store_bets')
    def test_handle_batch_fails_if_storage_fails(self, mock_store):
        bets = [
            Bet(1, "Juan", "Perez", 12345678, "1990-01-01", 7574),
            Bet(2, "Maria", "Gomez", 87654321, "1995-05-05", 1234)
        ]
        mock_store.side_effect = Exception("Storage error")
        self._prepare_proto(ActionType.REGISTER_BATCH_OF_BETS, bets, is_batch=True)

        self.handler.start()

        mock_store.assert_called_once_with(bets)
        self.proto.send_bet_registered.assert_not_called()
        self.assertTrue(any("result: fail" in str(c) for c in self.mock_log.mock_calls))
        self.mock_socket.close.assert_called()

if __name__ == '__main__':
    unittest.main()