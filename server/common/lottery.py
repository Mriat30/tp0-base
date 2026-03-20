from model.bet import has_won, load_bets
from model.lottery_winner import LotteryWinner

class Lottery:
    def __init__(self, total_agencys, logger):
        self._agencies_done = {}
        self._total_agencys = total_agencys
        self._logger = logger

    def notify_done(self, agency_id: int, protocol):
        self._agencies_done[agency_id] = protocol

        if len(self._agencies_done) == self._total_agencys:
            self._run_lottery_and_notify()
            return True
        return False
    
    def wait_for_ack(self, protocol):
        try:
            action = protocol.read_action()
            from common.utils import OpCode
            if action != OpCode.ACK_WINNERS:
                raise Exception(f"Expected ACK_WINNERS, got {action}")
        except Exception as e:
            self._logger.error(f"Error waiting for ACK: {e}")
            raise

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