from threading import Lock
from model.bet import store_bets, load_bets

class BetStorage:
    DEFAULT_BUFFER_SIZE = 1000

    def __init__(self, buffer_size=DEFAULT_BUFFER_SIZE):
        self._lock = Lock()
        self._buffer = []
        self._buffer_size = buffer_size

    def store(self, bets):
        with self._lock:
            self._buffer.extend(bets)
            if len(self._buffer) >= self._buffer_size:
                self._flush_locked()

    def load(self):
        with self._lock:
            return list(load_bets())

    def flush(self):
        with self._lock:
            self._flush_locked()

    def _flush_locked(self):
        if self._buffer:
            store_bets(self._buffer)
            self._buffer = []