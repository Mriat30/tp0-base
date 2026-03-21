from model.bet import has_won, load_bets, store_bets
from model.lottery_winner import LotteryWinner
from threading import Lock, Condition

class Lottery:
    def __init__(self, total_agencies, logger):
        self._agencies_done = set()
        self._total_agencies = total_agencies
        self._logger = logger
        self._storage_lock = Lock()   
        self._condition = Condition()
        self._winners = None

    def store_bets(self, bets):
        with self._storage_lock:
            store_bets(bets)

    def notify_done(self, agency_id):
        with self._condition:
            self._agencies_done.add(agency_id)
            if len(self._agencies_done) == self._total_agencies:
                self._winners = self._load_bets_safe()
                self._logger.info("action: sorteo | result: success")
                self._condition.notify_all()
            else:
                self._condition.wait_for(lambda: self._winners is not None)

        return [
            LotteryWinner(bet.document)
            for bet in self._winners
            if bet.agency == agency_id and has_won(bet)
        ]

    def _load_bets_safe(self):
        with self._storage_lock:
            return list(load_bets())