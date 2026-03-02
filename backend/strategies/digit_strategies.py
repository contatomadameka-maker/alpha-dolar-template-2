"""
ALPHA DOLAR 2.0 - Estratégias de Dígitos
Compatível com alpha_bot_api_production.py
FREE: Alpha Bot 4 | VIP: Digit Sniper, Digit Pulse | PREMIUM: Mega Digit 1.0, 2.0
"""
from collections import Counter, deque

# ==================== BASE STRATEGY ====================
try:
    from .base_strategy import BaseStrategy
except ImportError:
    try:
        from backend.strategies.base_strategy import BaseStrategy
    except ImportError:
        class BaseStrategy:
            def __init__(self, name=""):
                self.name = name
                self.ticks_history = deque(maxlen=500)
                self.last_signal = None
                self.signal_count = 0
            def update_tick(self, tick_data):
                self.ticks_history.append(tick_data)

try:
    from ..__init__ import BotConfig  # noqa
except Exception:
    pass
try:
    from ..config import BotConfig
except ImportError:
    try:
        from backend.config import BotConfig
    except ImportError:
        class BotConfig:
            DEFAULT_SYMBOL = "R_10"
            BASIS = "stake"
            STAKE_INICIAL = 0.35


# ==================== BASE DIGIT ====================
class _DigitBase(BaseStrategy):

    TRADING_MODE_CONFIG = {
        'lowRisk':  {'min_confidence': 0.72, 'cooldown': 20},
        'accurate': {'min_confidence': 0.68, 'cooldown': 14},
        'balanced': {'min_confidence': 0.64, 'cooldown': 10},
        'faster':   {'min_confidence': 0.60, 'cooldown':  6},
    }
    RISK_MODE_CONFIG = {
        'fixed':        {'martingale': False, 'multiplier': 1.0, 'max_steps': 0},
        'conservative': {'martingale': True,  'multiplier': 1.5, 'max_steps': 2},
        'optimized':    {'martingale': True,  'multiplier': 2.0, 'max_steps': 3},
        'aggressive':   {'martingale': True,  'multiplier': 2.5, 'max_steps': 5},
    }

    def __init__(self, name, trading_mode='faster', risk_mode='conservative'):
        super().__init__(name=name)
        self.digit_history = deque(maxlen=300)
        self._last_barrier = 5
        self._last_direction = 'OVER'
        self.last_signal_tick = 0

        tm = self.TRADING_MODE_CONFIG.get(trading_mode, self.TRADING_MODE_CONFIG['faster'])
        self.min_confidence = tm['min_confidence']
        self.cooldown_ticks = tm['cooldown']
        self.trading_mode   = trading_mode

        rm = self.RISK_MODE_CONFIG.get(risk_mode, self.RISK_MODE_CONFIG['conservative'])
        self.usar_martingale          = rm['martingale']
        self.multiplicador_martingale = rm['multiplier']
        self.max_martingale_steps     = rm['max_steps']
        self.risk_mode       = risk_mode
        self.martingale_step = 0
        self.stake_atual     = BotConfig.STAKE_INICIAL

    def on_trade_result(self, won: bool):
        if not self.usar_martingale:
            self.stake_atual = BotConfig.STAKE_INICIAL
            return
        if won:
            self.martingale_step = 0
            self.stake_atual = BotConfig.STAKE_INICIAL
        else:
            if self.martingale_step < self.max_martingale_steps:
                self.martingale_step += 1
                self.stake_atual = round(
                    BotConfig.STAKE_INICIAL * (self.multiplicador_martingale ** self.martingale_step), 2)
            else:
                self.martingale_step = 0
                self.stake_atual = BotConfig.STAKE_INICIAL

    def get_stake(self):
        return self.stake_atual

    def _get_digit(self, price):
        return int(str(float(price)).replace('.', '')[-1])

    def _freq(self, digits):
        c = Counter(digits)
        t = len(digits)
        return {d: c.get(d, 0) / t * 100 for d in range(10)}

    def _best_barrier(self, freq):
        best = None
        for barrier in range(1, 9):
            po = sum(freq.get(d, 0) for d in range(barrier + 1, 10))
            pu = sum(freq.get(d, 0) for d in range(0, barrier))
            direction  = 'OVER' if po >= pu else 'UNDER'
            confidence = max(po, pu)
            if best is None or confidence > best[2]:
                best = (barrier, direction, confidence)
        return best

    def _cooldown_ok(self):
        return (len(self.ticks_history) - self.last_signal_tick) >= self.cooldown_ticks

    def get_contract_params(self, direction):
        return {
            'contract_type': direction,
            'duration': 1, 'duration_unit': 't',
            'symbol': BotConfig.DEFAULT_SYMBOL,
            'basis': BotConfig.BASIS,
            'barrier': self._last_barrier,
        }

    def _emit_signal(self, direction, barrier, confidence):
        self._last_barrier    = barrier
        self._last_direction  = direction
        self.last_signal_tick = len(self.ticks_history)
        contract = 'DIGITOVER' if direction == 'OVER' else 'DIGITUNDER'
        self.last_signal  = contract
        self.signal_count += 1
        return True, contract, round(confidence / 100, 4)


# ==================== ALPHA BOT 4 — FREE ====================
class AlphaBot4Digit(_DigitBase):
    """Frequência básica dos últimos 100 dígitos com barreira ótima"""
    MIN_TICKS = 50

    def __init__(self, trading_mode='faster', risk_mode='conservative'):
        super().__init__("Alpha Bot 4 - Digit Pattern", trading_mode, risk_mode)
        print(f"⚙️ Alpha Bot 4 Digit | Modo: {trading_mode} | Confiança: {self.min_confidence:.0%}")

    def should_enter(self, tick_data):
        self.update_tick(tick_data)
        self.digit_history.append(self._get_digit(float(tick_data.get('quote', 0))))
        if len(self.digit_history) < self.MIN_TICKS or not self._cooldown_ok():
            return False, None, 0.0
        freq = self._freq(list(self.digit_history)[-100:])
        barrier, direction, confidence = self._best_barrier(freq)
        if confidence / 100 >= self.min_confidence:
            return self._emit_signal(direction, barrier, confidence)
        return False, None, 0.0

    def get_info(self):
        return {'name': self.name, 'tier': 'FREE', 'win_rate': '70%',
                'trading_mode': self.trading_mode, 'risk_mode': self.risk_mode}


# ==================== DIGIT SNIPER — VIP ====================
class DigitSniper(_DigitBase):
    """Entra contra o dígito mais quente do mercado"""
    MIN_TICKS = 60

    def __init__(self, trading_mode='faster', risk_mode='conservative'):
        super().__init__("Digit Sniper", trading_mode, risk_mode)
        print(f"⚙️ Digit Sniper | Modo: {trading_mode} | Confiança: {self.min_confidence:.0%}")

    def should_enter(self, tick_data):
        self.update_tick(tick_data)
        self.digit_history.append(self._get_digit(float(tick_data.get('quote', 0))))
        if len(self.digit_history) < self.MIN_TICKS or not self._cooldown_ok():
            return False, None, 0.0
        freq    = self._freq(list(self.digit_history)[-100:])
        hottest = max(freq, key=freq.get)
        coldest = min(freq, key=freq.get)
        if hottest >= 5:
            barrier    = hottest - 1
            direction  = 'UNDER'
            confidence = sum(freq.get(d, 0) for d in range(0, barrier))
        else:
            barrier    = hottest + 1
            direction  = 'OVER'
            confidence = sum(freq.get(d, 0) for d in range(barrier + 1, 10))
        cold_bonus = max(0, (10.0 - freq.get(coldest, 10)) * 0.5)
        confidence = min(confidence + cold_bonus, 95.0)
        if confidence / 100 >= self.min_confidence:
            return self._emit_signal(direction, barrier, confidence)
        return False, None, 0.0

    def get_info(self):
        return {'name': self.name, 'tier': 'VIP', 'win_rate': '73%',
                'trading_mode': self.trading_mode, 'risk_mode': self.risk_mode}


# ==================== DIGIT PULSE — VIP ====================
class DigitPulse(_DigitBase):
    """Detecta pulsos de dígitos altos/baixos e entra na reversão"""
    MIN_TICKS   = 40
    PULSE_WIN   = 8
    PULSE_THRES = 6

    def __init__(self, trading_mode='faster', risk_mode='conservative'):
        super().__init__("Digit Pulse", trading_mode, risk_mode)
        print(f"⚙️ Digit Pulse | Modo: {trading_mode} | Confiança: {self.min_confidence:.0%}")

    def should_enter(self, tick_data):
        self.update_tick(tick_data)
        self.digit_history.append(self._get_digit(float(tick_data.get('quote', 0))))
        if len(self.digit_history) < self.MIN_TICKS or not self._cooldown_ok():
            return False, None, 0.0
        recent = list(self.digit_history)[-self.PULSE_WIN:]
        highs  = sum(1 for d in recent if d > 4)
        lows   = len(recent) - highs
        if highs >= self.PULSE_THRES:
            barrier, direction = 5, 'UNDER'
            confidence = 50 + (highs - self.PULSE_THRES) * 8.0
        elif lows >= self.PULSE_THRES:
            barrier, direction = 4, 'OVER'
            confidence = 50 + (lows - self.PULSE_THRES) * 8.0
        else:
            return False, None, 0.0
        confidence = min(confidence, 90.0)
        if confidence / 100 >= self.min_confidence:
            return self._emit_signal(direction, barrier, confidence)
        return False, None, 0.0

    def get_info(self):
        return {'name': self.name, 'tier': 'VIP', 'win_rate': '72%',
                'trading_mode': self.trading_mode, 'risk_mode': self.risk_mode}


# ==================== MEGA DIGIT 1.0 — PREMIUM ====================
class MegaDigit1(_DigitBase):
    """Score combinado: frequência (40%) + pulso (35%) + par/ímpar (25%)"""
    MIN_TICKS = 70

    def __init__(self, trading_mode='faster', risk_mode='conservative'):
        super().__init__("Mega Digit 1.0", trading_mode, risk_mode)
        print(f"⚙️ Mega Digit 1.0 | Modo: {trading_mode} | Confiança: {self.min_confidence:.0%}")

    def should_enter(self, tick_data):
        self.update_tick(tick_data)
        self.digit_history.append(self._get_digit(float(tick_data.get('quote', 0))))
        if len(self.digit_history) < self.MIN_TICKS or not self._cooldown_ok():
            return False, None, 0.0
        digits = list(self.digit_history)

        freq = self._freq(digits[-100:])
        barrier, freq_dir, freq_conf = self._best_barrier(freq)
        freq_score = (freq_conf - 50) * 0.8

        recent = digits[-10:]
        highs  = sum(1 for d in recent if d > 4)
        lows   = len(recent) - highs
        if highs > lows:
            pulse_dir   = 'UNDER'
            pulse_score = (highs / 10 - 0.5) * 70
        else:
            pulse_dir   = 'OVER'
            pulse_score = (lows / 10 - 0.5) * 70

        pi_conf  = max(
            sum(1 for d in digits[-50:] if d % 2 == 0),
            sum(1 for d in digits[-50:] if d % 2 != 0)
        ) / 50 * 100
        pi_score = (pi_conf - 50) * 0.5

        total     = min(50 + (freq_score * 0.40 + pulse_score * 0.35 + pi_score * 0.25), 95)
        direction = freq_dir if freq_dir == pulse_dir else freq_dir

        if total / 100 >= self.min_confidence:
            return self._emit_signal(direction, barrier, total)
        return False, None, 0.0

    def get_info(self):
        return {'name': self.name, 'tier': 'PREMIUM', 'win_rate': '75%',
                'trading_mode': self.trading_mode, 'risk_mode': self.risk_mode}


# ==================== MEGA DIGIT 2.0 — PREMIUM ====================
class MegaDigit2(_DigitBase):
    """Janelas deslizantes 25/50/100 ticks com pesos 50%/30%/20%"""
    MIN_TICKS = 100

    def __init__(self, trading_mode='faster', risk_mode='conservative'):
        super().__init__("Mega Digit 2.0", trading_mode, risk_mode)
        print(f"⚙️ Mega Digit 2.0 | Modo: {trading_mode} | Confiança: {self.min_confidence:.0%}")

    def _analyze_window(self, digits, size):
        w = digits[-size:]
        if len(w) < size // 2:
            return None
        return self._best_barrier(self._freq(w))

    def should_enter(self, tick_data):
        self.update_tick(tick_data)
        self.digit_history.append(self._get_digit(float(tick_data.get('quote', 0))))
        if len(self.digit_history) < self.MIN_TICKS or not self._cooldown_ok():
            return False, None, 0.0
        digits  = list(self.digit_history)
        windows = [
            (self._analyze_window(digits, 25),  0.50),
            (self._analyze_window(digits, 50),  0.30),
            (self._analyze_window(digits, 100), 0.20),
        ]
        windows = [(w, p) for w, p in windows if w is not None]
        if not windows:
            return False, None, 0.0
        votes         = {'OVER': 0.0, 'UNDER': 0.0}
        barrier_votes = {}
        for (b, d, c), weight in windows:
            votes[d] += weight * c
            barrier_votes[(b, d)] = barrier_votes.get((b, d), 0) + weight
        best_dir   = max(votes, key=votes.get)
        total_w    = sum(p for _, p in windows)
        confidence = votes[best_dir] / total_w if total_w else 0
        best_barrier = max(
            ((b, d) for (b, d) in barrier_votes if d == best_dir),
            key=lambda x: barrier_votes[x],
            default=(5, best_dir)
        )[0]
        if confidence / 100 >= self.min_confidence:
            return self._emit_signal(best_dir, best_barrier, confidence)
        return False, None, 0.0

    def get_info(self):
        return {'name': self.name, 'tier': 'PREMIUM', 'win_rate': '76%',
                'trading_mode': self.trading_mode, 'risk_mode': self.risk_mode}
