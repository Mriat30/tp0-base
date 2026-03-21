from model.bet import has_won, load_bets, store_bets
from model.lottery_winner import LotteryWinner
from threading import Lock, Condition

class Lottery:
    def __init__(self, total_agencies, logger):
        self._agencies_done = set()
        self._total_agencies = total_agencies
        self._logger = logger
        self._lock = Lock()
        self._lottery_done = Condition(self._lock)
        self._winners = None

    def store_bets(self, bets):
        with self._lock:
            store_bets(bets)

    def notify_done(self, agency_id):
        with self._lottery_done:
            self._agencies_done.add(agency_id)
            if len(self._agencies_done) == self._total_agencies:
                self._winners = list(load_bets())
                self._logger.info("action: sorteo | result: success")
                self._lottery_done.notify_all()
            else:
                self._lottery_done.wait_for(lambda: self._winners is not None)

        return [
            LotteryWinner(bet.document)
            for bet in self._winners
            if bet.agency == agency_id and has_won(bet)
        ]