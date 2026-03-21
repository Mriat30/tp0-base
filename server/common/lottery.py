from model.bet import has_won, load_bets
from model.lottery_winner import LotteryWinner

class Lottery:
    def __init__(self, total_agencies, logger):
        self._agencies_done = {}
        self._total_agencies = total_agencies
        self._logger = logger

    def notify_done(self, agency_id: int, protocol):
        self._agencies_done[agency_id] = protocol
        if len(self._agencies_done) == self._total_agencies:
            self._run_lottery_and_notify()

    def _run_lottery_and_notify(self):
        all_bets = list(load_bets())
        self._logger.info("action: sorteo | result: success")

        for agency_id, protocol in self._agencies_done.items():
            winners = [
                LotteryWinner(bet.document)
                for bet in all_bets
                if bet.agency == agency_id and has_won(bet)
            ]
            protocol.send_winners(winners)
            protocol.close()