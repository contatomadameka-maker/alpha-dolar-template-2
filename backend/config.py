"""
Configurações do Deriv Bot
Baseado no DC Bots
"""
from enum import Enum

class TradingMode(Enum):
    """Modos de negociação disponíveis"""
    BAIXO_RISCO = "baixo_risco"      # Máxima precisão, menos negociações
    PRECISO = "preciso"               # Menos negociações, mais precisão
    BALANCEADO = "balanceado"         # Negociações e precisão balanceada
    VELOZ = "veloz"                   # Mais negociações, menos precisão

class RiskManagement(Enum):
    """Tipos de gerenciamento de risco"""
    QUANTIA_FIXA = "quantia_fixa"     # Baixo risco (min $10)
    CONSERVADOR = "conservador"        # Baixo risco (min $50)
    OTIMIZADO = "otimizado"           # Médio risco (min $100)
    AGRESSIVO = "agressivo"           # Alto risco (min $200)

class BotConfig:
    """Configuração principal do bot"""

    # ===== API DERIV =====
    # COLE SEU TOKEN AQUI ENTRE AS ASPAS ↓
    API_TOKEN = "a1-TD8gXQ9R8UGFLMH3rrfrJdtYQkN8k"
    APP_ID = "128988"

    # ===== MERCADO =====
    DEFAULT_SYMBOL = "R_100"  # Volatility 100 Index

    # ===== ESTRATÉGIA =====
    DEFAULT_STRATEGY = "dc_bot_1"

    # ===== MODO DE NEGOCIAÇÃO =====
    TRADING_MODE = TradingMode.VELOZ

    # ===== GESTÃO DE RISCO =====
    RISK_MANAGEMENT = RiskManagement.CONSERVADOR
    STAKE_INICIAL = 0.35      # Quantia inicial ($)
    LUCRO_ALVO = 2.0          # Stop gain ($)
    LIMITE_PERDA = 5.0        # Stop loss ($)

    # ===== MARTINGALE =====
    USAR_MARTINGALE = True
    MULTIPLICADOR_MARTINGALE = 2.0  # Dobra após perda
    MAX_MARTINGALE_STEPS = 3        # Máximo de tentativas

    # ===== CONTRATO =====
    DURATION = 1              # 1 tick
    DURATION_UNIT = "t"       # t = ticks, m = minutes, h = hours
    BASIS = "stake"           # stake ou payout

    # ===== LIMITES =====
    MAX_TRADES_PER_DAY = 1000
    MIN_BALANCE = 0.50        # Saldo mínimo para operar

    # ===== MODO DE STOP LOSS =====
    STOP_LOSS_TYPE = "value"  # "value" ou "consecutive_losses"
    MAX_CONSECUTIVE_LOSSES = 5  # Parar após X perdas seguidas

    # ===== LOGGING =====
    LOG_LEVEL = "INFO"        # DEBUG, INFO, WARNING, ERROR
    LOG_TO_FILE = True
    LOG_FILE = "alpha_dolar.log"

    # ===== INFORMAÇÕES DO BOT =====
    BOT_NAME = "Alpha Dolar 2.0"
    BOT_VERSION = "2.0.0"
    BOT_AUTHOR = "Dirlei Luis"

class StrategyConfig:
    """Configurações específicas por estratégia"""

    DC_BOT_1 = {
        "name": "DC Bot 1",
        "type": "rise_fall",
        "min_balance": 10.0,
        "recommended_mode": TradingMode.VELOZ,
    }

    DC_BOT_2 = {
        "name": "DC Bot 2",
        "type": "digits",
        "min_balance": 10.0,
        "recommended_mode": TradingMode.BALANCEADO,
    }

    ALPHA_MIND = {
        "name": "AlphaMind",
        "type": "advanced",
        "min_balance": 100.0,
        "recommended_mode": TradingMode.PRECISO,
        "vip": True,
    }

class MarketConfig:
    """Configuração de mercados disponíveis"""

    VOLATILITY_INDICES = {
        "R_10": {"name": "Volatility 10 Index", "tick_interval": 2},
        "R_25": {"name": "Volatility 25 Index", "tick_interval": 2},
        "R_50": {"name": "Volatility 50 Index", "tick_interval": 2},
        "R_75": {"name": "Volatility 75 Index", "tick_interval": 2},
        "R_100": {"name": "Volatility 100 Index", "tick_interval": 2},
        "1HZ10V": {"name": "Volatility 10 (1s) Index", "tick_interval": 1},
        "1HZ25V": {"name": "Volatility 25 (1s) Index", "tick_interval": 1},
        "1HZ50V": {"name": "Volatility 50 (1s) Index", "tick_interval": 1},
        "1HZ75V": {"name": "Volatility 75 (1s) Index", "tick_interval": 1},
        "1HZ100V": {"name": "Volatility 100 (1s) Index", "tick_interval": 1},
    }

    JUMP_INDICES = {
        "JD10": {"name": "Jump 10 Index"},
        "JD25": {"name": "Jump 25 Index"},
        "JD50": {"name": "Jump 50 Index"},
        "JD75": {"name": "Jump 75 Index"},
        "JD100": {"name": "Jump 100 Index"},
    }

    CRASH_BOOM = {
        "BOOM1000": {"name": "Boom 1000 Index"},
        "BOOM500": {"name": "Boom 500 Index"},
        "CRASH1000": {"name": "Crash 1000 Index"},
        "CRASH500": {"name": "Crash 500 Index"},
    }

# ===== VALIDAÇÕES =====
def validate_config():
    """Valida as configurações antes de iniciar o bot"""
    errors = []

    if BotConfig.API_TOKEN == "COLE_SEU_TOKEN_AQUI":
        errors.append("⚠️ Configure seu API_TOKEN da Deriv!")

    if BotConfig.STAKE_INICIAL < 0.35:
        errors.append("⚠️ Stake inicial muito baixo! Mínimo: $0.35")

    if BotConfig.STAKE_INICIAL > BotConfig.MIN_BALANCE and False:  # desabilitado
        errors.append("⚠️ Stake inicial maior que saldo mínimo!")

    if BotConfig.LUCRO_ALVO <= 0:
        errors.append("⚠️ Lucro alvo deve ser maior que zero!")

    if BotConfig.LIMITE_PERDA <= 0:
        errors.append("⚠️ Limite de perda deve ser maior que zero!")

    if errors:
        print("\n❌ ERROS DE CONFIGURAÇÃO:\n")
        for error in errors:
            print(f"  {error}")
        print("\n")
        return False

    print("✅ Configurações validadas com sucesso!")
    return True

if __name__ == "__main__":
    # Teste de validação
    validate_config()