import unittest
from unittest.mock import MagicMock, patch
from common.lottery import Lottery
from model.bet import Bet
from model.lottery_winner import LotteryWinner
import datetime


class TestLottery(unittest.TestCase):
    def setUp(self):
        self.mock_logger = MagicMock()
        self.lottery = Lottery(total_agencies=2, logger=self.mock_logger)

    def tearDown(self):
        pass

    @patch('common.lottery.load_bets')
    @patch('common.lottery.has_won')
    def test_notify_done_runs_lottery_when_all_agencies_done(self, mock_has_won, mock_load_bets):
        bets = [
            Bet(1, "Juan", "Perez", "12345678", "1990-01-01", 7574),      # Agency 1, Winner
            Bet(1, "Maria", "Gomez", "87654321", "1995-05-05", 1234),     # Agency 1, Loser
            Bet(2, "Carlos", "Lopez", "11111111", "1985-03-15", 7574),    # Agency 2, Winner
        ]
        mock_load_bets.return_value = bets

        mock_has_won.side_effect = lambda bet: bet.number == 7574

        protocol_agency_1 = MagicMock()
        protocol_agency_2 = MagicMock()

        self.lottery.notify_done(1, protocol_agency_1)
        
        protocol_agency_1.send_winners.assert_not_called()

        self.lottery.notify_done(2, protocol_agency_2)

        agency_1_call_args = protocol_agency_1.send_winners.call_args[0][0]
        self.assertEqual(len(agency_1_call_args), 1)
        self.assertIsInstance(agency_1_call_args[0], LotteryWinner)
        self.assertEqual(agency_1_call_args[0].document, "12345678")

        agency_2_call_args = protocol_agency_2.send_winners.call_args[0][0]
        self.assertEqual(len(agency_2_call_args), 1)
        self.assertIsInstance(agency_2_call_args[0], LotteryWinner)
        self.assertEqual(agency_2_call_args[0].document, "11111111")

        self.assertTrue(any("sorteo" in str(call) for call in self.mock_logger.info.call_args_list))


if __name__ == '__main__':
    unittest.main()
