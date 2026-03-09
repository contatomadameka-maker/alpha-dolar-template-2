"""
Módulo de Estratégias de Trading
Alpha Dolar 2.0
"""
from .base_strategy import BaseStrategy
from .alpha_bot_1 import AlphaBot1, AlphaBot1Reverse, AlphaBot1MA
from .alpha_bot_4_digit import AlphaBot4DigitPattern
from .digit_sniper import DigitSniper
from .digit_pulse import DigitPulse
from .mega_digit import MegaDigit1, MegaDigit2

__all__ = [
    # Base
    'BaseStrategy',
    # Rise/Fall
    'AlphaBot1',
    'AlphaBot1Reverse',
    'AlphaBot1MA',
    # Dígitos FREE
    'AlphaBot4DigitPattern',
    # Dígitos VIP
    'DigitSniper',
    'DigitPulse',
    # Dígitos PREMIUM
    'MegaDigit1',
    'MegaDigit2',
]

# Mapa de estratégias por chave (usado pelos painéis)
STRATEGY_MAP = {
    # Rise/Fall
    "alpha_bot_1":  AlphaBot1,
    "alpha_bot_2":  AlphaBot1Reverse,
    "alpha_bot_3":  AlphaBot1MA,
    # Dígitos FREE
    "alpha_bot_4":  AlphaBot4DigitPattern,
    # Dígitos VIP
    "digit_sniper": DigitSniper,
    "digit_pulse":  DigitPulse,
    # Dígitos PREMIUM
    "mega_digit_1": MegaDigit1,
    "mega_digit_2": MegaDigit2,
}

def get_strategy(key):
    """Retorna instância da estratégia pelo nome"""
    cls = STRATEGY_MAP.get(key)
    if cls is None:
        raise ValueError(f"Estratégia '{key}' não encontrada. Disponíveis: {list(STRATEGY_MAP.keys())}")
    return cls()