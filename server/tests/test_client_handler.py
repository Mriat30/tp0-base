import unittest
from unittest.mock import MagicMock
from network.client_handler import ClientHandler
from network.protocol import OpCode
from model.bet import Bet

class TestClientHandler(unittest.TestCase):
    def setUp(self):
        self.mock_socket = MagicMock()
        self.mock_socket.getpeername.return_value = ('127.0.0.1', 12345)
        self.mock_protocol = MagicMock()
        self.mock_protocol._socket = self.mock_socket
        self.mock_log = MagicMock()
        self.mock_lottery = MagicMock()
        self.handler = ClientHandler(self.mock_protocol, self.mock_lottery, logger=self.mock_log)
        self.proto = self.mock_protocol
        self.proto.send_bet_registered = MagicMock()

    def _prepare_proto(self, action, return_val, is_batch=False):
        self.proto.read_action = MagicMock(side_effect=[OpCode.CLIENT_ID, action, EOFError])

        def mock_read_client_id():
            self.proto._client_id = 1
            return 1

        self.proto.read_client_id = MagicMock(side_effect=mock_read_client_id)
        if is_batch:
            self.proto.read_batch_of_bets = MagicMock(return_value=return_val)
        else:
            self.proto.read_bet = MagicMock(return_value=return_val)

    def test_handle_single_bet_success(self):
        bet = Bet(1, "Juan", "Perez", "12345678", "1990-01-01", "7574")
        self._prepare_proto(OpCode.REGISTER_SINGLE_BET, bet)

        self.handler.start()

        self.mock_lottery.store.assert_called_once_with([bet])
        self.proto.send_bet_registered.assert_called_once()
        self.proto.close.assert_called_once()

    def test_handle_batch_bets_success(self):
        bets = [
            Bet(1, "Juan", "Perez", "12345678", "1990-01-01", "7574"),
            Bet(1, "Maria", "Gomez", "87654321", "1995-05-05", "1234"),
        ]
        self._prepare_proto(OpCode.REGISTER_BATCH_OF_BETS, bets, is_batch=True)

        self.handler.start()

        self.mock_lottery.store.assert_called_once_with(bets)
        self.proto.send_bet_registered.assert_called_once()
        self.proto.close.assert_called_once()

    def test_handle_batch_bets_fail_if_storage_fails(self):
        bets = [
            Bet(1, "Juan", "Perez", "12345678", "1990-01-01", "7574"),
            Bet(1, "Maria", "Gomez", "87654321", "1995-05-05", "1234"),
        ]
        self.mock_lottery.store.side_effect = OSError("Storage error")
        self._prepare_proto(OpCode.REGISTER_BATCH_OF_BETS, bets, is_batch=True)

        self.handler.start()

        self.mock_lottery.store.assert_called_once_with(bets)
        self.proto.send_bet_registered.assert_not_called()
        self.assertTrue(any("result: fail" in str(c) for c in self.mock_log.mock_calls))
        self.proto.close.assert_called()

    def test_handle_invalid_handshake_opcode(self):
        self.proto.read_action = MagicMock(return_value=OpCode.REGISTER_SINGLE_BET)

        self.handler.start()

        self.proto.read_client_id.assert_not_called()
        self.mock_lottery.store.assert_not_called()
        self.proto.send_bet_registered.assert_not_called()
        self.assertTrue(any("result: fail" in str(c) for c in self.mock_log.mock_calls))
        self.proto.close.assert_called_once()

if __name__ == '__main__':
    unittest.main()