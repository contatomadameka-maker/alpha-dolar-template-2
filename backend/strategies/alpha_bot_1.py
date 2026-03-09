"""
Alpha Bot 1 - Estratégia Rise/Fall
Alpha Dolar 2.0
"""
from .base_strategy import BaseStrategy

try:
    from ..config import BotConfig
except ImportError:
    from config import BotConfig

class AlphaBot1(BaseStrategy):
    """
    Estratégia Alpha Bot 1 - Rise/Fall Simples

    Lógica:
    - Analisa tendência dos últimos N ticks
    - Entra em CALL se tendência de alta
    - Entra em PUT se tendência de baixa
    - Usa confirmação de padrão consecutivo
    """

    def __init__(self, lookback_period=5, min_consecutive=2, confidence_threshold=0.6):
        super().__init__(name="Alpha Bot 1")

        self.lookback_period = lookback_period
        self.min_consecutive = min_consecutive
        self.confidence_threshold = confidence_threshold

    def should_enter(self, tick_data):
        """Decide se deve entrar em trade"""
        if not self.is_ready():
            return False, None, 0.0

        self.update_tick(tick_data)

        trend = self.calculate_trend(self.lookback_period)
        pattern = self.detect_pattern("consecutive")

        if trend == "UP":
            consecutive = pattern.get("consecutive_ups", 0)
            if consecutive >= self.min_consecutive:
                confidence = min(consecutive / (self.lookback_period * 1.5), 1.0)

                if confidence >= self.confidence_threshold:
                    self.last_signal = "CALL"
                    self.signal_count += 1
                    return True, "CALL", confidence

        elif trend == "DOWN":
            consecutive = pattern.get("consecutive_downs", 0)
            if consecutive >= self.min_consecutive:
                confidence = min(consecutive / (self.lookback_period * 1.5), 1.0)

                if confidence >= self.confidence_threshold:
                    self.last_signal = "PUT"
                    self.signal_count += 1
                    return True, "PUT", confidence

        return False, None, 0.0

    def get_contract_params(self, direction):
        """Retorna parâmetros do contrato"""
        return {
            "contract_type": direction,
            "duration": BotConfig.DURATION,
            "duration_unit": BotConfig.DURATION_UNIT,
            "symbol": BotConfig.DEFAULT_SYMBOL,
            "basis": BotConfig.BASIS
        }

class AlphaBot1Reverse(BaseStrategy):
    """
    Alpha Bot 1 Reverso - Estratégia de Reversão
    Entra CONTRA a tendência
    """

    def __init__(self, lookback_period=5, min_consecutive=3):
        super().__init__(name="Alpha Bot 1 Reverse")
        self.lookback_period = lookback_period
        self.min_consecutive = min_consecutive

    def should_enter(self, tick_data):
        """Lógica reversa - entra contra a tendência"""
        if not self.is_ready():
            return False, None, 0.0

        self.update_tick(tick_data)

        trend = self.calculate_trend(self.lookback_period)
        pattern = self.detect_pattern("consecutive")

        if trend == "DOWN":
            consecutive = pattern.get("consecutive_downs", 0)
            if consecutive >= self.min_consecutive:
                confidence = min(consecutive / (self.lookback_period * 2), 1.0)
                self.last_signal = "CALL"
                self.signal_count += 1
                return True, "CALL", confidence

        elif trend == "UP":
            consecutive = pattern.get("consecutive_ups", 0)
            if consecutive >= self.min_consecutive:
                confidence = min(consecutive / (self.lookback_period * 2), 1.0)
                self.last_signal = "PUT"
                self.signal_count += 1
                return True, "PUT", confidence

        return False, None, 0.0

    def get_contract_params(self, direction):
        """Parâmetros do contrato"""
        return {
            "contract_type": direction,
            "duration": BotConfig.DURATION,
            "duration_unit": BotConfig.DURATION_UNIT,
            "symbol": BotConfig.DEFAULT_SYMBOL,
            "basis": BotConfig.BASIS
        }

class AlphaBot1MA(BaseStrategy):
    """
    Alpha Bot 1 MA - Estratégia com Médias Móveis
    Usa SMA e EMA para confirmar tendência
    """

    def __init__(self, sma_period=10, ema_period=5):
        super().__init__(name="Alpha Bot 1 MA")
        self.sma_period = sma_period
        self.ema_period = ema_period
        self.last_sma = None

    def should_enter(self, tick_data):
        """Lógica com médias móveis"""
        if not self.is_ready():
            return False, None, 0.0

        self.update_tick(tick_data)

        current_price = float(tick_data.get('quote', 0))
        sma = self.get_sma(self.sma_period)
        ema = self.get_ema(self.ema_period)

        if sma is None or ema is None:
            return False, None, 0.0

        sma_trend = "NEUTRAL"
        if self.last_sma is not None:
            if sma > self.last_sma:
                sma_trend = "UP"
            elif sma < self.last_sma:
                sma_trend = "DOWN"

        self.last_sma = sma

        if current_price > sma and sma_trend == "UP" and current_price > ema:
            confidence = min((current_price - sma) / sma, 0.9)
            self.last_signal = "CALL"
            self.signal_count += 1
            return True, "CALL", confidence

        elif current_price < sma and sma_trend == "DOWN" and current_price < ema:
            confidence = min((sma - current_price) / sma, 0.9)
            self.last_signal = "PUT"
            self.signal_count += 1
            return True, "PUT", confidence

        return False, None, 0.0

    def get_contract_params(self, direction):
        """Parâmetros do contrato"""
        return {
            "contract_type": direction,
            "duration": BotConfig.DURATION,
            "duration_unit": BotConfig.DURATION_UNIT,
            "symbol": BotConfig.DEFAULT_SYMBOL,
            "basis": BotConfig.BASIS
        }