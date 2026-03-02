"""
Alpha Bot 4 - Digit Pattern Analysis (FREE)
Analisa frequência dos últimos 100 dígitos e encontra barreira ótima.
"""
from collections import Counter, deque

# Import flexível — funciona tanto como módulo quanto standalone
try:
    from .base_strategy import BaseStrategy
except ImportError:
    try:
        from strategies.base_strategy import BaseStrategy
    except ImportError:
        import sys, os
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from strategies.base_strategy import BaseStrategy

try:
    from ..config import BotConfig
except ImportError:
    try:
        from config import BotConfig
    except ImportError:
        class BotConfig:
            DEFAULT_SYMBOL = "R_100"
            BASIS = "stake"


class AlphaBot4DigitPattern(BaseStrategy):
    def __init__(self):
        super().__init__(name="Alpha Bot 4 - Digit Pattern")
        self.tier = "FREE"
        self.contract_type = "DIGITOVER/DIGITUNDER"
        self.digit_history = deque(maxlen=200)
        self.min_ticks = 50
        self.min_confidence = 60.0
        self._last_barrier = 5
        self._last_direction = "OVER"

    def _get_last_digit(self, price):
        return int(str(float(price)).replace(".", "")[-1])

    def _calc_frequency(self, digits):
        c = Counter(digits)
        t = len(digits)
        return {d: c.get(d, 0) / t * 100 for d in range(10)}

    def _find_best_barrier(self, frequency):
        best = None
        for barrier in range(1, 9):
            prob_over  = sum(frequency.get(d, 0) for d in range(barrier + 1, 10))
            prob_under = sum(frequency.get(d, 0) for d in range(0, barrier))
            direction, confidence = ("OVER", prob_over) if prob_over >= prob_under else ("UNDER", prob_under)
            if best is None or confidence > best[2]:
                best = (barrier, direction, confidence)
        return best

    def should_enter(self, tick_data):
        self.update_tick(tick_data)
        self.digit_history.append(self._get_last_digit(float(tick_data.get("quote", 0))))
        if len(self.digit_history) < self.min_ticks:
            return False, None, 0.0
        freq = self._calc_frequency(list(self.digit_history)[-100:])
        barrier, direction, confidence = self._find_best_barrier(freq)
        self._last_barrier = barrier
        self._last_direction = direction
        if confidence >= self.min_confidence:
            contract = "DIGITOVER" if direction == "OVER" else "DIGITUNDER"
            self.last_signal = contract
            self.signal_count += 1
            return True, contract, round(confidence / 100, 4)
        return False, None, 0.0

    def get_contract_params(self, direction):
        return {"contract_type": direction, "symbol": BotConfig.DEFAULT_SYMBOL,
                "duration": 1, "duration_unit": "t", "basis": BotConfig.BASIS,
                "barrier": self._last_barrier}

    def analyze(self, ticks):
        if len(ticks) < self.min_ticks:
            return {"signal": None, "reason": f"Aguardando dados ({len(ticks)}/{self.min_ticks})", "confidence": 0}
        digits = [self._get_last_digit(float(t)) for t in ticks[-100:]]
        self.digit_history.extend(digits)
        freq = self._calc_frequency(digits)
        barrier, direction, confidence = self._find_best_barrier(freq)
        self._last_barrier = barrier
        self._last_direction = direction
        if confidence >= self.min_confidence:
            contract = "DIGITOVER" if direction == "OVER" else "DIGITUNDER"
            cold = [d for d, f in freq.items() if f < 8.0]
            return {"signal": contract, "contract_type": contract, "barrier": barrier,
                    "confidence": round(confidence, 2),
                    "reason": f"Digit{direction} {barrier} | {confidence:.1f}% | Frios: {cold}",
                    "parameters": {"contract_type": contract, "duration": 1, "duration_unit": "t",
                                   "symbol": BotConfig.DEFAULT_SYMBOL, "basis": BotConfig.BASIS, "barrier": barrier}}
        return {"signal": None, "confidence": round(confidence, 2),
                "reason": f"Confiança insuficiente ({confidence:.1f}% < {self.min_confidence}%)"}

    def get_info(self):
        return {"name": self.name, "tier": self.tier, "contract_type": self.contract_type,
                "description": "Frequência de dígitos com barreira ótima", "min_ticks": self.min_ticks}

    def reset_state(self):
        self.digit_history.clear()
        self.last_signal = None
        self.signal_count = 0
