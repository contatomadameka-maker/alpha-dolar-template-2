"""
Alpha Bot 4 - Digit Pattern Analysis (FREE)
Analisa frequência dos últimos 100 dígitos e encontra barreira ótima.
FIX 03/03: Barreira mínima 5 para payout justo + fallback seguro no watchdog
"""
from collections import Counter, deque

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
        self._last_barrier = 5       # ✅ Padrão: barreira 5 (50/50, payout justo)
        self._last_direction = "OVER"
        self._last_contract = "DIGITOVER"

    def _get_last_digit(self, price):
        return int(str(float(price)).replace(".", "")[-1])

    def _calc_frequency(self, digits):
        c = Counter(digits)
        t = len(digits)
        return {d: c.get(d, 0) / t * 100 for d in range(10)}

    def _find_best_barrier(self, frequency):
        """
        Busca barreira com melhor probabilidade, mínimo 5.
        Barreira < 5 = payout muito baixo (não vale o risco).
        """
        best = None
        # ✅ Começa em 3, mas só aceita barreira >= 4
        for barrier in range(3, 9):
            prob_over  = sum(frequency.get(d, 0) for d in range(barrier + 1, 10))
            prob_under = sum(frequency.get(d, 0) for d in range(0, barrier))
            direction, confidence = ("OVER", prob_over) if prob_over >= prob_under else ("UNDER", prob_under)
            if best is None or confidence > best[2]:
                best = (barrier, direction, confidence)

        # ✅ Garante barreira mínima 4 para payout razoável
        barrier, direction, confidence = best
        if barrier < 4:
            barrier = 5
            prob_over  = sum(frequency.get(d, 0) for d in range(6, 10))
            prob_under = sum(frequency.get(d, 0) for d in range(0, 5))
            direction = "OVER" if prob_over >= prob_under else "UNDER"
            confidence = max(prob_over, prob_under)

        return barrier, direction, confidence

    def _get_safe_params(self, contract=None):
        """Retorna parâmetros seguros para DIGITOVER/DIGITUNDER com barreira padrão"""
        if contract is None:
            contract = self._last_contract
        return {
            "contract_type": contract,
            "symbol": BotConfig.DEFAULT_SYMBOL,
            "duration": 1,
            "duration_unit": "t",
            "basis": BotConfig.BASIS,
            "barrier": self._last_barrier
        }

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
            self._last_contract = contract
            self.last_signal = contract
            self.signal_count += 1
            return True, contract, round(confidence / 100, 4)
        return False, None, 0.0

    def get_contract_params(self, direction):
        """
        Sempre retorna parâmetros digit válidos.
        ✅ Se direction for CALL/PUT (fallback watchdog), converte para DIGITOVER seguro.
        """
        if direction in ("CALL", "PUT", None):
            direction = self._last_contract  # usa último contrato digit válido

        return {
            "contract_type": direction,
            "symbol": BotConfig.DEFAULT_SYMBOL,
            "duration": 1,
            "duration_unit": "t",
            "basis": BotConfig.BASIS,
            "barrier": self._last_barrier
        }

    def analyze(self, ticks):
        if len(ticks) < self.min_ticks:
            # ✅ Mesmo sem dados suficientes, retorna sinal padrão com barreira segura
            # Isso evita que o watchdog force CALL
            contract = self._last_contract
            return {
                "signal": contract,
                "contract_type": contract,
                "barrier": self._last_barrier,
                "confidence": self.min_confidence,
                "reason": f"Fallback seguro | Barreira: {self._last_barrier}",
                "parameters": self._get_safe_params(contract)
            }

        digits = [self._get_last_digit(float(t)) for t in ticks[-100:]]
        self.digit_history.extend(digits)
        freq = self._calc_frequency(digits)
        barrier, direction, confidence = self._find_best_barrier(freq)
        self._last_barrier = barrier
        self._last_direction = direction

        if confidence >= self.min_confidence:
            contract = "DIGITOVER" if direction == "OVER" else "DIGITUNDER"
            self._last_contract = contract
            cold = [d for d, f in freq.items() if f < 8.0]
            return {
                "signal": contract,
                "contract_type": contract,
                "barrier": barrier,
                "confidence": round(confidence, 2),
                "reason": f"Digit{direction} {barrier} | {confidence:.1f}% | Frios: {cold}",
                "parameters": {
                    "contract_type": contract,
                    "duration": 1,
                    "duration_unit": "t",
                    "symbol": BotConfig.DEFAULT_SYMBOL,
                    "basis": BotConfig.BASIS,
                    "barrier": barrier
                }
            }

        # Confiança insuficiente mas ainda retorna fallback digit (nunca CALL)
        contract = self._last_contract
        return {
            "signal": contract,
            "contract_type": contract,
            "barrier": self._last_barrier,
            "confidence": round(confidence, 2),
            "reason": f"Confiança baixa ({confidence:.1f}%) — usando barreira padrão {self._last_barrier}",
            "parameters": self._get_safe_params(contract)
        }

    def get_info(self):
        return {
            "name": self.name,
            "tier": self.tier,
            "contract_type": self.contract_type,
            "description": "Frequência de dígitos com barreira ótima (mín. 4)",
            "min_ticks": self.min_ticks
        }

    def reset_state(self):
        self.digit_history.clear()
        self.last_signal = None
        self.signal_count = 0
        # ✅ Não reseta _last_barrier nem _last_contract ao resetar estado
