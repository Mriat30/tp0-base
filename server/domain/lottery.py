from threading import Condition
from model.bet import has_won
from model.lottery_winner import LotteryWinner
from model.bet import load_bets, store_bets

class Lottery:
    def __init__(self, total_agencies, logger):
        self._total_agencies = total_agencies
        self._logger = logger
        self._condition = Condition()
        self._agencies_done = set()
        self._winners = {}
        self._lottery_done = False

    def store(self, bets):
        with self._condition:
            store_bets(bets)

    def notify_done(self, agency_id):
        with self._condition:
            self._agencies_done.add(agency_id)
            if len(self._agencies_done) == self._total_agencies:
                self._run_lottery()
                self._lottery_done = True
                self._condition.notify_all()

    def get_winners(self, agency_id):
        with self._condition:
            self._condition.wait_for(lambda: self._lottery_done)
            return [LotteryWinner(doc) for doc in self._winners.get(agency_id, [])]

    def _run_lottery(self):
        all_bets = load_bets()
        for bet in all_bets:
            if has_won(bet):
                self._winners.setdefault(bet.agency, []).append(bet.document)
        self._logger.info("action: sorteo | result: success")