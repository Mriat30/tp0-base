from threading import Barrier, BrokenBarrierError
from collections import defaultdict
from model.bet import has_won
from model.lottery_winner import LotteryWinner

class Lottery:
    def __init__(self, total_agencies, storage, logger):
        self._total_agencies = total_agencies
        self._storage = storage
        self._logger = logger
        self._winners = defaultdict(set)
        self._barrier = Barrier(total_agencies, action=self._run_lottery)

    def notify_done(self, agency_id):
        try:
            self._barrier.wait()
            return [LotteryWinner(doc) for doc in self._winners.get(agency_id, [])]
        except BrokenBarrierError:
            self._logger.error(f"La barrera se rompió mientras esperaba a la agencia {agency_id}")
            return []

    def _run_lottery(self):
        all_bets = self._storage.load()
        
        for bet in all_bets:
            if has_won(bet):
                self._winners[bet.agency].add(bet.document)
        
        self._logger.info("action: sorteo | result: success")