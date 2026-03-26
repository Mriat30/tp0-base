from threading import Event, Lock
from model.bet import has_won
from model.lottery_winner import LotteryWinner

class Lottery:
    def __init__(self, total_agencies, storage, logger):
        self._agencies_done = set()
        self._total_agencies = total_agencies
        self._logger = logger
        self._storage = storage
        self._lottery_ready = Event()
        self._lock = Lock()
        self._winners = {}

    def notify_done(self, agency_id):
        with self._lock:
            self._agencies_done.add(agency_id)
            if len(self._agencies_done) == self._total_agencies:
                self._run_lottery()

    def get_winners(self, agency_id):
        self._lottery_ready.wait()
        return [
            LotteryWinner(doc)
            for doc in self._winners.get(agency_id, [])
        ]

    def _run_lottery(self):
        self._storage.flush()
        all_bets = self._storage.load()
        for bet in all_bets:
            if has_won(bet):
                self._winners.setdefault(bet.agency, []).append(bet.document)
        self._logger.info("action: sorteo | result: success")
        self._lottery_ready.set()