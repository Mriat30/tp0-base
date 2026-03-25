from threading import Lock
from server.model.bet import store_bets, load_bets

class BetStorage:
    def __init__(self):
        self._lock = Lock()

    def store(self, bets):
        with self._lock:
            store_bets(bets)

    def load(self):
        with self._lock:
            return list(load_bets())