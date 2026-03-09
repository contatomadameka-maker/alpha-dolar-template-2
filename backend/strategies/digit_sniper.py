"""
Digit Sniper - Estratégia VIP de Dígitos
Foca no dígito MAIS FRIO e entra com barreira exata (Under X ou Over X).
Lógica: quando um dígito específico está muito abaixo de 10%, ele tende a aparecer.
Entra com Over/Under de forma a EXCLUIR o dígito mais quente.
"""
from collections import Counter, deque
try:
    from .base_strategy import BaseStrategy
    from ..config import BotConfig
except ImportError:
    from base_strategy import BaseStrategy
    from config import BotConfig

class DigitSniper(BaseStrategy):
    def __init__(self):
        super().__init__(name="Digit Sniper")
        self.tier = "VIP"
        self.contract_type = "DIGITOVER/DIGITUNDER"
        self.digit_history = deque(maxlen=300)
        self.min_ticks = 60
        self.min_confidence = 62.0
        self._last_barrier = 5
        self._last_direction = "OVER"

    def _get_last_digit(self, price):
        return int(str(float(price)).replace(".", "")[-1])

    def _calc_frequency(self, digits):
        c = Counter(digits)
        t = len(digits)
        return {d: c.get(d, 0) / t * 100 for d in range(10)}

    def _snipe(self, freq):
        """
        Estratégia Sniper: identifica o dígito MAIS QUENTE e
        entra para que ele NÃO apareça — ou seja, entra no lado oposto.
        """
        hottest = max(freq, key=freq.get)
        coldest = min(freq, key=freq.get)

        # Se o dígito mais quente for alto (6-9), entra UNDER hottest-1
        # Se o dígito mais quente for baixo (0-3), entra OVER hottest+1
        if hottest >= 5:
            barrier = hottest - 1
            direction = "UNDER"
            # confiança = freq acumulada dos dígitos < barrier
            confidence = sum(freq.get(d, 0) for d in range(0, barrier))
        else:
            barrier = hottest + 1
            direction = "OVER"
            confidence = sum(freq.get(d, 0) for d in range(barrier + 1, 10))

        # Bonus de confiança se o dígito frio está muito abaixo de 10%
        cold_bonus = max(0, (10.0 - freq.get(coldest, 10)) * 0.5)
        confidence = min(confidence + cold_bonus, 95.0)

        return barrier, direction, confidence

    def should_enter(self, tick_data):
        self.update_tick(tick_data)
        self.digit_history.append(self._get_last_digit(float(tick_data.get("quote", 0))))
        if len(self.digit_history) < self.min_ticks:
            return False, None, 0.0
        freq = self._calc_frequency(list(self.digit_history)[-100:])
        barrier, direction, confidence = self._snipe(freq)
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
        barrier, direction, confidence = self._snipe(freq)
        self._last_barrier = barrier
        self._last_direction = direction
        hottest = max(freq, key=freq.get)
        coldest = min(freq, key=freq.get)
        if confidence >= self.min_confidence:
            contract = "DIGITOVER" if direction == "OVER" else "DIGITUNDER"
            return {"signal": contract, "contract_type": contract, "barrier": barrier,
                    "confidence": round(confidence, 2),
                    "reason": f"Sniper {direction} {barrier} | Quente: {hottest}({freq[hottest]:.1f}%) | Frio: {coldest}({freq[coldest]:.1f}%)",
                    "parameters": {"contract_type": contract, "duration": 1, "duration_unit": "t",
                                   "symbol": BotConfig.DEFAULT_SYMBOL, "basis": BotConfig.BASIS, "barrier": barrier}}
        return {"signal": None, "confidence": round(confidence, 2),
                "reason": f"Sniper aguardando desequilíbrio maior ({confidence:.1f}%)"}

    def get_info(self):
        return {"name": self.name, "tier": self.tier, "contract_type": self.contract_type,
                "description": "Sniper: entra contra o dígito mais quente", "min_ticks": self.min_ticks}

    def reset_state(self):
        self.digit_history.clear()
        self.last_signal = None
        self.signal_count = 0