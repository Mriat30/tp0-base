import unittest
from unittest.mock import MagicMock, patch
from common.lottery import Lottery
from model.bet import Bet
from model.lottery_winner import LotteryWinner
import threading

class TestLottery(unittest.TestCase):
    def setUp(self):
        self.mock_logger = MagicMock()
        self.mock_storage = MagicMock()
        self.lottery = Lottery(total_agencies=2, storage=self.mock_storage, logger=self.mock_logger)

    @patch('common.lottery.has_won')
    def test_notify_done_returns_winners_when_all_agencies_done(self, mock_has_won):
        bets = [
            Bet(1, "Juan", "Perez", "12345678", "1990-01-01", 7574),
            Bet(1, "Maria", "Gomez", "87654321", "1995-05-05", 1234),
            Bet(2, "Carlos", "Lopez", "11111111", "1985-03-15", 7574),
        ]
        self.mock_storage.load.return_value = bets
        mock_has_won.side_effect = lambda bet: bet.number == 7574

        results = {}

        def agency_task(agency_id):
            winners = self.lottery.notify_done(agency_id)
            results[agency_id] = winners

        t1 = threading.Thread(target=agency_task, args=(1,))
        t2 = threading.Thread(target=agency_task, args=(2,))
        
        t1.start()
        t2.start()
        
        t1.join(timeout=5.0)
        t2.join(timeout=5.0)

        self.assertFalse(t1.is_alive())
        self.assertFalse(t2.is_alive())

        winners_agency_1 = results[1]
        self.assertEqual(len(winners_agency_1), 1)
        self.assertIsInstance(winners_agency_1[0], LotteryWinner)
        self.assertEqual(winners_agency_1[0].document, "12345678")

        winners_agency_2 = results[2]
        self.assertEqual(len(winners_agency_2), 1)
        self.assertIsInstance(winners_agency_2[0], LotteryWinner)
        self.assertEqual(winners_agency_2[0].document, "11111111")

        log_calls = [call.args[0] for call in self.mock_logger.info.call_args_list]
        self.assertTrue(any("sorteo" in msg for msg in log_calls))

if __name__ == '__main__':
    unittest.main()