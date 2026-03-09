"""
Mega Digit 1.0 / 2.0 - Estratégias Premium de Dígitos

Mega Digit 1.0: Combina frequência + pulso + par/ímpar em score unificado.
Mega Digit 2.0: Janelas deslizantes (25/50/100 ticks) com pesos diferentes —
                mais peso para o mais recente, menos para o histórico.
"""
from collections import Counter, deque
try:
    from .base_strategy import BaseStrategy
    from ..config import BotConfig
except ImportError:
    from base_strategy import BaseStrategy
    from config import BotConfig


class MegaDigit1(BaseStrategy):
    """Mega Digit 1.0 — Score combinado: frequência + pulso + par/ímpar"""

    def __init__(self):
        super().__init__(name="Mega Digit 1.0")
        self.tier = "PREMIUM"
        self.contract_type = "DIGITOVER/DIGITUNDER"
        self.digit_history = deque(maxlen=300)
        self.min_ticks = 70
        self.min_score = 65.0
        self._last_barrier = 5
        self._last_direction = "OVER"

    def _get_last_digit(self, price):
        return int(str(float(price)).replace(".", "")[-1])

    def _combined_score(self, digits):
        """
        Calcula score combinado de 3 fontes:
        1. Frequência (40%): barreira ótima por desequilíbrio
        2. Pulso (35%): dominância recente de um lado
        3. Par/Ímpar (25%): desequilíbrio par vs ímpar
        """
        # --- 1. Frequência ---
        c = Counter(digits[-100:])
        t = len(digits[-100:])
        freq = {d: c.get(d, 0) / t * 100 for d in range(10)}

        best_freq = None
        for barrier in range(1, 9):
            po = sum(freq.get(d, 0) for d in range(barrier + 1, 10))
            pu = sum(freq.get(d, 0) for d in range(0, barrier))
            direction = "OVER" if po >= pu else "UNDER"
            confidence = max(po, pu)
            if best_freq is None or confidence > best_freq[2]:
                best_freq = (barrier, direction, confidence)

        freq_barrier, freq_dir, freq_conf = best_freq
        freq_score = (freq_conf - 50) * 0.8  # normaliza para 0-40

        # --- 2. Pulso (últimos 10) ---
        recent = digits[-10:]
        highs = sum(1 for d in recent if d > 4)
        lows  = len(recent) - highs
        if highs > lows:
            pulse_dir = "UNDER"
            pulse_barrier = 5
            pulse_score = (highs / len(recent) - 0.5) * 70
        else:
            pulse_dir = "OVER"
            pulse_barrier = 4
            pulse_score = (lows / len(recent) - 0.5) * 70

        # --- 3. Par/Ímpar ---
        pares   = sum(1 for d in digits[-50:] if d % 2 == 0)
        impares = len(digits[-50:]) - pares
        if pares > impares:
            pi_conf = pares / len(digits[-50:]) * 100
        else:
            pi_conf = impares / len(digits[-50:]) * 100
        pi_score = (pi_conf - 50) * 0.5

        # --- Score final ponderado ---
        total_score = (freq_score * 0.40) + (pulse_score * 0.35) + (pi_score * 0.25)
        total_score = max(0, min(total_score, 45))  # cap em 45 pontos extras

        final_confidence = 50 + total_score

        # Direção: decide por maioria (freq + pulso)
        if freq_dir == pulse_dir:
            direction = freq_dir
            barrier = freq_barrier
        else:
            # desempate: usa a que tem maior score individual
            if abs(freq_conf - 50) >= abs(pulse_score):
                direction = freq_dir
                barrier = freq_barrier
            else:
                direction = pulse_dir
                barrier = pulse_barrier

        return barrier, direction, round(final_confidence, 2)

    def should_enter(self, tick_data):
        self.update_tick(tick_data)
        self.digit_history.append(self._get_last_digit(float(tick_data.get("quote", 0))))
        if len(self.digit_history) < self.min_ticks:
            return False, None, 0.0
        barrier, direction, confidence = self._combined_score(list(self.digit_history))
        self._last_barrier = barrier
        self._last_direction = direction
        if confidence >= self.min_score:
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
        digits = [self._get_last_digit(float(t)) for t in ticks]
        self.digit_history.extend(digits)
        barrier, direction, confidence = self._combined_score(digits)
        self._last_barrier = barrier
        self._last_direction = direction
        if confidence >= self.min_score:
            contract = "DIGITOVER" if direction == "OVER" else "DIGITUNDER"
            return {"signal": contract, "contract_type": contract, "barrier": barrier,
                    "confidence": confidence,
                    "reason": f"Mega Score {confidence:.1f}% | {direction} {barrier} | Freq+Pulso+Par",
                    "parameters": {"contract_type": contract, "duration": 1, "duration_unit": "t",
                                   "symbol": BotConfig.DEFAULT_SYMBOL, "basis": BotConfig.BASIS, "barrier": barrier}}
        return {"signal": None, "confidence": confidence,
                "reason": f"Score insuficiente ({confidence:.1f}% < {self.min_score}%)"}

    def get_info(self):
        return {"name": self.name, "tier": self.tier, "contract_type": self.contract_type,
                "description": "Score combinado: frequência + pulso + par/ímpar", "min_ticks": self.min_ticks}

    def reset_state(self):
        self.digit_history.clear()
        self.last_signal = None
        self.signal_count = 0


class MegaDigit2(BaseStrategy):
    """Mega Digit 2.0 — Janelas deslizantes com pesos (25/50/100 ticks)"""

    def __init__(self):
        super().__init__(name="Mega Digit 2.0")
        self.tier = "PREMIUM"
        self.contract_type = "DIGITOVER/DIGITUNDER"
        self.digit_history = deque(maxlen=300)
        self.min_ticks = 100
        self.min_confidence = 66.0
        self._last_barrier = 5
        self._last_direction = "OVER"

    def _get_last_digit(self, price):
        return int(str(float(price)).replace(".", "")[-1])

    def _analyze_window(self, digits, size):
        """Analisa uma janela de N dígitos e retorna (barrier, direction, confidence)"""
        window = digits[-size:]
        if len(window) < size // 2:
            return None
        c = Counter(window)
        t = len(window)
        freq = {d: c.get(d, 0) / t * 100 for d in range(10)}
        best = None
        for barrier in range(1, 9):
            po = sum(freq.get(d, 0) for d in range(barrier + 1, 10))
            pu = sum(freq.get(d, 0) for d in range(0, barrier))
            direction = "OVER" if po >= pu else "UNDER"
            confidence = max(po, pu)
            if best is None or confidence > best[2]:
                best = (barrier, direction, confidence)
        return best

    def _weighted_analysis(self, digits):
        """
        Combina 3 janelas com pesos:
        - Últimos 25 ticks: peso 50% (mais recente = mais relevante)
        - Últimos 50 ticks: peso 30%
        - Últimos 100 ticks: peso 20%
        """
        w25  = self._analyze_window(digits, 25)
        w50  = self._analyze_window(digits, 50)
        w100 = self._analyze_window(digits, 100)

        windows = [(w25, 0.50), (w50, 0.30), (w100, 0.20)]
        windows = [(w, p) for w, p in windows if w is not None]

        if not windows:
            return None

        # Vota na direção com maior peso
        votes = {"OVER": 0.0, "UNDER": 0.0}
        barrier_votes = {}
        for (barrier, direction, confidence), weight in windows:
            votes[direction] += weight * confidence
            key = (barrier, direction)
            barrier_votes[key] = barrier_votes.get(key, 0) + weight

        best_direction = max(votes, key=votes.get)
        best_barrier = max(
            ((b, d) for (b, d) in barrier_votes if d == best_direction),
            key=lambda x: barrier_votes[x],
            default=(5, best_direction)
        )[0]

        final_confidence = votes[best_direction] / sum(
            p for _, p in windows
        )
        return best_barrier, best_direction, round(final_confidence, 2)

    def should_enter(self, tick_data):
        self.update_tick(tick_data)
        self.digit_history.append(self._get_last_digit(float(tick_data.get("quote", 0))))
        if len(self.digit_history) < self.min_ticks:
            return False, None, 0.0
        result = self._weighted_analysis(list(self.digit_history))
        if result is None:
            return False, None, 0.0
        barrier, direction, confidence = result
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
        digits = [self._get_last_digit(float(t)) for t in ticks]
        self.digit_history.extend(digits)
        result = self._weighted_analysis(digits)
        if result is None:
            return {"signal": None, "confidence": 0, "reason": "Janelas insuficientes"}
        barrier, direction, confidence = result
        self._last_barrier = barrier
        self._last_direction = direction
        if confidence >= self.min_confidence:
            contract = "DIGITOVER" if direction == "OVER" else "DIGITUNDER"
            return {"signal": contract, "contract_type": contract, "barrier": barrier,
                    "confidence": confidence,
                    "reason": f"Janelas 25/50/100 convergem: {direction} {barrier} | {confidence:.1f}%",
                    "parameters": {"contract_type": contract, "duration": 1, "duration_unit": "t",
                                   "symbol": BotConfig.DEFAULT_SYMBOL, "basis": BotConfig.BASIS, "barrier": barrier}}
        return {"signal": None, "confidence": confidence,
                "reason": f"Janelas divergentes ou confiança baixa ({confidence:.1f}%)"}

    def get_info(self):
        return {"name": self.name, "tier": self.tier, "contract_type": self.contract_type,
                "description": "Janelas 25/50/100 com pesos 50%/30%/20%", "min_ticks": self.min_ticks}

    def reset_state(self):
        self.digit_history.clear()
        self.last_signal = None
        self.signal_count = 0