"""
Digit Pulse - Estratégia VIP de Dígitos
Detecta sequências e pulsos: quando o mesmo lado (alto/baixo) domina
os últimos N ticks, entra na reversão esperada.
"""
from collections import deque
try:
    from .base_strategy import BaseStrategy
    from ..config import BotConfig
except ImportError:
    from base_strategy import BaseStrategy
    from config import BotConfig

class DigitPulse(BaseStrategy):
    def __init__(self):
        super().__init__(name="Digit Pulse")
        self.tier = "VIP"
        self.contract_type = "DIGITOVER/DIGITUNDER"
        self.digit_history = deque(maxlen=200)
        self.min_ticks = 40
        self.pulse_window = 8   # janela para detectar pulso
        self.pulse_threshold = 6  # quantos do mesmo lado para acionar
        self._last_barrier = 4
        self._last_direction = "OVER"

    def _get_last_digit(self, price):
        return int(str(float(price)).replace(".", "")[-1])

    def _detect_pulse(self, digits):
        """
        Analisa os últimos N dígitos.
        Se >= pulse_threshold forem altos (>4), entra UNDER.
        Se >= pulse_threshold forem baixos (<5), entra OVER.
        Retorna (barrier, direction, confidence).
        """
        recent = list(digits)[-self.pulse_window:]
        if len(recent) < self.pulse_window:
            return None

        highs = sum(1 for d in recent if d > 4)
        lows  = sum(1 for d in recent if d < 5)

        if highs >= self.pulse_threshold:
            # Muitos dígitos altos — reversão para baixo
            barrier = 5
            direction = "UNDER"
            confidence = 50 + (highs - self.pulse_threshold) * 8.0
        elif lows >= self.pulse_threshold:
            # Muitos dígitos baixos — reversão para cima
            barrier = 4
            direction = "OVER"
            confidence = 50 + (lows - self.pulse_threshold) * 8.0
        else:
            return None

        confidence = min(confidence, 90.0)
        return barrier, direction, confidence

    def should_enter(self, tick_data):
        self.update_tick(tick_data)
        self.digit_history.append(self._get_last_digit(float(tick_data.get("quote", 0))))
        if len(self.digit_history) < self.min_ticks:
            return False, None, 0.0
        result = self._detect_pulse(self.digit_history)
        if result is None:
            return False, None, 0.0
        barrier, direction, confidence = result
        self._last_barrier = barrier
        self._last_direction = direction
        if confidence >= 58.0:
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
        digits = [self._get_last_digit(float(t)) for t in ticks[-50:]]
        self.digit_history.extend(digits)
        result = self._detect_pulse(self.digit_history)
        if result is None:
            recent = list(self.digit_history)[-self.pulse_window:]
            highs = sum(1 for d in recent if d > 4)
            return {"signal": None, "confidence": 0,
                    "reason": f"Sem pulso detectado (altos: {highs}/{self.pulse_window})"}
        barrier, direction, confidence = result
        self._last_barrier = barrier
        self._last_direction = direction
        if confidence >= 58.0:
            contract = "DIGITOVER" if direction == "OVER" else "DIGITUNDER"
            recent = list(self.digit_history)[-self.pulse_window:]
            return {"signal": contract, "contract_type": contract, "barrier": barrier,
                    "confidence": round(confidence, 2),
                    "reason": f"Pulso detectado! {direction} {barrier} | Últimos {self.pulse_window}: {recent}",
                    "parameters": {"contract_type": contract, "duration": 1, "duration_unit": "t",
                                   "symbol": BotConfig.DEFAULT_SYMBOL, "basis": BotConfig.BASIS, "barrier": barrier}}
        return {"signal": None, "confidence": round(confidence, 2), "reason": "Pulso fraco"}

    def get_info(self):
        return {"name": self.name, "tier": self.tier, "contract_type": self.contract_type,
                "description": "Detecta pulsos e entra na reversão", "min_ticks": self.min_ticks}

    def reset_state(self):
        self.digit_history.clear()
        self.last_signal = None
        self.signal_count = 0