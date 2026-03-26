from threading import Thread, Event
from queue import Queue
from model.bet import has_won
from model.lottery_winner import LotteryWinner

class Lottery:
    def __init__(self, total_agencies, storage, logger):
        self._total_agencies = total_agencies
        self._logger = logger
        self._storage = storage
        self._lottery_ready = Event()
        self._winners = {}
        self._queue = Queue()
        self._thread = Thread(target=self._worker)
        self._thread.start()

    def notify_done(self, agency_id):
        self._queue.put(agency_id)

    def get_winners(self, agency_id):
        self._lottery_ready.wait()
        return [LotteryWinner(doc) for doc in self._winners.get(agency_id, [])]

    def _worker(self):
        agencies_done = set()
        while len(agencies_done) < self._total_agencies:
            agency_id = self._queue.get()
            agencies_done.add(agency_id)
        self._run_lottery()

    def _run_lottery(self):
        self._storage.flush()
        all_bets = self._storage.load()
        for bet in all_bets:
            if has_won(bet):
                self._winners.setdefault(bet.agency, []).append(bet.document)
        self._logger.info("action: sorteo | result: success")
        self._lottery_ready.set()