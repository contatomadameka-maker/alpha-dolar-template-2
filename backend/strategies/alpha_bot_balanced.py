"""
Alpha Bot Balanced - Estratégia Intermediária
Balanceada entre velocidade e precisão
Win Rate esperado: 55-60%
Frequência: 2-5 trades/hora

v2.0 — Suporte a trading_mode e risk_mode do frontend
"""
from .base_strategy import BaseStrategy
from ..config import BotConfig
import statistics

class AlphaBotBalanced(BaseStrategy):
    """Estratégia balanceada - nem muito lenta, nem muito agressiva"""

    # ====== MAPA DE MODOS DE NEGOCIAÇÃO ======
    # Cada modo define: confiança mínima, cooldown e condições mínimas
    TRADING_MODE_CONFIG = {
        'lowRisk':  {'min_confidence': 0.90, 'cooldown': 20, 'min_conditions': 4},  # Baixo risco — máxima precisão
        'accurate': {'min_confidence': 0.80, 'cooldown': 14, 'min_conditions': 4},  # Preciso
        'balanced': {'min_confidence': 0.70, 'cooldown': 10, 'min_conditions': 3},  # Balanceado
        'faster':   {'min_confidence': 0.60, 'cooldown':  6, 'min_conditions': 3},  # Veloz — mais trades
    }

    # ====== MAPA DE GERENCIAMENTO DE RISCO ======
    # Cada modo define: martingale ativo, multiplicador e máximo de passos
    RISK_MODE_CONFIG = {
        'fixed':        {'martingale': False, 'multiplier': 1.0,  'max_steps': 0},  # Quantia fixa
        'conservative': {'martingale': True,  'multiplier': 1.5,  'max_steps': 2},  # Conservador
        'optimized':    {'martingale': True,  'multiplier': 2.0,  'max_steps': 3},  # Otimizado
        'aggressive':   {'martingale': True,  'multiplier': 2.5,  'max_steps': 5},  # Agressivo
    }

    def __init__(self, trading_mode='faster', risk_mode='conservative'):
        super().__init__(name="Alpha Bot Balanced")
        self.min_history = 20
        self.last_signal_tick = 0

        # Aplica modo de negociação
        tm = self.TRADING_MODE_CONFIG.get(trading_mode, self.TRADING_MODE_CONFIG['faster'])
        self.min_confidence  = tm['min_confidence']
        self.cooldown_ticks  = tm['cooldown']
        self.min_conditions  = tm['min_conditions']
        self.trading_mode    = trading_mode

        # Aplica gerenciamento de risco
        rm = self.RISK_MODE_CONFIG.get(risk_mode, self.RISK_MODE_CONFIG['conservative'])
        self.usar_martingale        = rm['martingale']
        self.multiplicador_martingale = rm['multiplier']
        self.max_martingale_steps   = rm['max_steps']
        self.risk_mode              = risk_mode
        self.martingale_step        = 0
        self.stake_atual            = BotConfig.STAKE_INICIAL

        print(f"⚙️ Modo: {trading_mode} | Confiança mínima: {self.min_confidence:.0%} | Cooldown: {self.cooldown_ticks} ticks")
        print(f"🛡️ Risco: {risk_mode} | Martingale: {self.usar_martingale} | Multiplicador: {self.multiplicador_martingale}x | Máx passos: {self.max_martingale_steps}")

    def on_trade_result(self, won: bool):
        """Chamado após cada trade para atualizar o Martingale"""
        if not self.usar_martingale:
            self.stake_atual = BotConfig.STAKE_INICIAL
            return

        if won:
            # Vitória — reset
            self.martingale_step = 0
            self.stake_atual = BotConfig.STAKE_INICIAL
        else:
            # Derrota — aumenta stake se não atingiu máximo
            if self.martingale_step < self.max_martingale_steps:
                self.martingale_step += 1
                self.stake_atual = round(BotConfig.STAKE_INICIAL * (self.multiplicador_martingale ** self.martingale_step), 2)
                print(f"📈 Martingale passo {self.martingale_step}: stake = ${self.stake_atual}")
            else:
                # Máximo atingido — reset
                self.martingale_step = 0
                self.stake_atual = BotConfig.STAKE_INICIAL
                print(f"🔄 Martingale resetado após {self.max_martingale_steps} passos")

    def get_stake(self):
        """Retorna stake atual (com ou sem Martingale)"""
        return self.stake_atual

    def should_enter(self, tick_data):
        """
        Estratégia baseada em:
        - Momentum de curto prazo (últimos 10 ticks)
        - Reversão à média
        - Volatilidade moderada

        Confiança mínima e condições ajustadas pelo trading_mode.
        """
        self.update_tick(tick_data)

        if len(self.ticks_history) < self.min_history:
            return False, None, 0.0

        ticks_since_last = len(self.ticks_history) - self.last_signal_tick
        if ticks_since_last < self.cooldown_ticks:
            return False, None, 0.0

        try:
            recent_10 = self.ticks_history[-10:]
            recent_20 = self.ticks_history[-20:]

            current_price = recent_10[-1]
            ma_10 = statistics.mean(recent_10)
            ma_20 = statistics.mean(recent_20)
            momentum = (recent_10[-1] - recent_10[0]) / recent_10[0] * 100
            volatility = statistics.stdev(recent_10) if len(recent_10) > 1 else 0
            distance_from_ma = ((current_price - ma_20) / ma_20) * 100

            # Sinal de CALL
            call_conditions = [
                current_price < ma_20,
                momentum < -0.05,
                distance_from_ma < -0.15,
                volatility > 0.1
            ]

            # Sinal de PUT
            put_conditions = [
                current_price > ma_20,
                momentum > 0.05,
                distance_from_ma > 0.15,
                volatility > 0.1
            ]

            call_score = sum(call_conditions)
            put_score  = sum(put_conditions)

            if call_score >= self.min_conditions:
                confidence = (call_score / 4) * 0.85 + 0.15
                if confidence >= self.min_confidence:
                    self.last_signal_tick = len(self.ticks_history)
                    return True, "CALL", confidence

            if put_score >= self.min_conditions:
                confidence = (put_score / 4) * 0.85 + 0.15
                if confidence >= self.min_confidence:
                    self.last_signal_tick = len(self.ticks_history)
                    return True, "PUT", confidence

            return False, None, 0.0

        except Exception as e:
            print(f"⚠️ Erro na análise: {e}")
            return False, None, 0.0

    def get_contract_params(self, direction):
        return {
            "contract_type": direction,
            "duration": 1,
            "duration_unit": "t",
            "symbol": BotConfig.DEFAULT_SYMBOL,
            "basis": BotConfig.BASIS
        }

    def get_info(self):
        return {
            'name': self.name,
            'tier': 'Intermediária',
            'min_history': self.min_history,
            'cooldown': self.cooldown_ticks,
            'min_confidence': f"{self.min_confidence:.0%}",
            'trading_mode': self.trading_mode,
            'risk_mode': self.risk_mode,
            'martingale': self.usar_martingale,
            'expected_win_rate': '55-60%',
            'trades_per_hour': '2-5',
            'indicators': 'MA10, MA20, Momentum, Volatilidade',
            'risk_level': 'Médio'
        }