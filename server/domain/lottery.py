from threading import Condition
from model.bet import has_won
from model.lottery_winner import LotteryWinner

class Lottery:
    def __init__(self, total_agencies, storage, logger):
        self._total_agencies = total_agencies
        self._logger = logger
        self._storage = storage
        self._condition = Condition()
        self._agencies_done = set()
        self._winners = {}
        self._lottery_done = False

    def notify_done(self, agency_id):
        with self._condition:
            self._agencies_done.add(agency_id)
            should_run = len(self._agencies_done) == self._total_agencies

        if should_run:
            self._run_lottery()
            with self._condition:
                self._lottery_done = True
                self._condition.notify_all()

    def get_winners(self, agency_id):
        with self._condition:
            self._condition.wait_for(lambda: self._lottery_done)
            return [LotteryWinner(doc) for doc in self._winners.get(agency_id, [])]

    def _run_lottery(self):
        all_bets = self._storage.load()
        for bet in all_bets:
            if has_won(bet):
                self._winners.setdefault(bet.agency, []).append(bet.document)
        self._logger.info("action: sorteo | result: success")