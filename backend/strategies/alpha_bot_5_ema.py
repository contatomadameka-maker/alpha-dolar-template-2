"""
╔══════════════════════════════════════════════════════════╗
║         ALPHA BOT 5 - EMA CROSSOVER STRATEGY            ║
║                    GRATUITA (FREE)                       ║
╚══════════════════════════════════════════════════════════╝

ESTRATÉGIA:
- Usa cruzamento de EMAs (Exponential Moving Average)
- EMA rápida (9) vs EMA lenta (21)
- Tipo de contrato: CALL/PUT (Rise/Fall)
- Duração: 1 tick

SINAIS:
- CALL: Quando EMA rápida cruza ACIMA da EMA lenta
- PUT: Quando EMA rápida cruza ABAIXO da EMA lenta

INDICADORES:
- EMA 9 (rápida)
- EMA 21 (lenta)
- Distância entre EMAs (força do sinal)
"""

import pandas as pd
import numpy as np
from datetime import datetime


class AlphaBot5EMA:
    """Alpha Bot 5 - EMA Crossover Strategy"""

    def __init__(self):
        self.name = "Alpha Bot 5 - EMA Crossover"
        self.tier = "FREE"
        self.contract_type = "CALL/PUT"
        self.description = "Cruzamento de Médias Móveis Exponenciais"

        # Parâmetros das EMAs
        self.fast_period = 9
        self.slow_period = 21

        # Histórico
        self.last_fast_ema = None
        self.last_slow_ema = None

    def calculate_ema(self, prices, period):
        """
        Calcula EMA (Exponential Moving Average)

        Args:
            prices: Lista de preços
            period: Período da EMA

        Returns:
            pandas.Series: Valores da EMA
        """
        df = pd.DataFrame({'close': prices})
        ema = df['close'].ewm(span=period, adjust=False).mean()
        return ema

    def analyze(self, ticks):
        """
        Analisa os ticks e retorna sinal de trade

        Args:
            ticks: Lista de preços recentes (mínimo 30 ticks)

        Returns:
            dict: Resultado da análise
        """
        if len(ticks) < 30:
            return {
                'signal': None,
                'reason': 'Aguardando mais dados (mínimo 30 ticks)',
                'confidence': 0
            }

        # Pega últimos 50 ticks para cálculo
        recent_ticks = ticks[-50:] if len(ticks) > 50 else ticks
        prices = [float(tick) for tick in recent_ticks]

        # Calcula EMAs
        fast_ema = self.calculate_ema(prices, self.fast_period)
        slow_ema = self.calculate_ema(prices, self.slow_period)

        # Valores atuais
        current_fast = fast_ema.iloc[-1]
        current_slow = slow_ema.iloc[-1]

        # Valores anteriores
        prev_fast = fast_ema.iloc[-2]
        prev_slow = slow_ema.iloc[-2]

        # Calcula distância entre EMAs
        distance = abs(current_fast - current_slow)
        distance_pct = (distance / current_slow) * 100

        # Detecta cruzamento
        signal = None
        confidence = 0
        reason = ""

        # CALL: EMA rápida cruza ACIMA da EMA lenta
        if prev_fast <= prev_slow and current_fast > current_slow:
            signal = "CALL"
            # Confiança baseada na distância entre EMAs
            # Quanto maior a separação, maior a confiança
            confidence = min(100, 50 + (distance_pct * 500))
            reason = f"EMA{self.fast_period} cruzou ACIMA da EMA{self.slow_period} (Distância: {distance_pct:.3f}%)"

        # PUT: EMA rápida cruza ABAIXO da EMA lenta
        elif prev_fast >= prev_slow and current_fast < current_slow:
            signal = "PUT"
            confidence = min(100, 50 + (distance_pct * 500))
            reason = f"EMA{self.fast_period} cruzou ABAIXO da EMA{self.slow_period} (Distância: {distance_pct:.3f}%)"

        # Sem cruzamento recente
        else:
            # Verifica posição atual das EMAs
            if current_fast > current_slow:
                if distance_pct < 0.001:
                    reason = f"EMAs muito próximas - possível cruzamento em breve (Fast ACIMA)"
                else:
                    reason = f"EMA{self.fast_period} acima da EMA{self.slow_period} - tendência de alta"
            else:
                if distance_pct < 0.001:
                    reason = f"EMAs muito próximas - possível cruzamento em breve (Fast ABAIXO)"
                else:
                    reason = f"EMA{self.fast_period} abaixo da EMA{self.slow_period} - tendência de baixa"

        # Preço atual em relação às EMAs
        current_price = prices[-1]
        price_vs_fast = "acima" if current_price > current_fast else "abaixo"
        price_vs_slow = "acima" if current_price > current_slow else "abaixo"

        # Atualiza histórico
        self.last_fast_ema = current_fast
        self.last_slow_ema = current_slow

        return {
            'signal': signal,
            'contract_type': signal,
            'confidence': round(confidence, 2),
            'reason': reason,
            'indicators': {
                'ema_fast': round(current_fast, 2),
                'ema_slow': round(current_slow, 2),
                'distance': round(distance, 2),
                'distance_pct': round(distance_pct, 5),
                'current_price': round(current_price, 2),
                'price_vs_fast_ema': price_vs_fast,
                'price_vs_slow_ema': price_vs_slow,
                'trend': 'bullish' if current_fast > current_slow else 'bearish'
            },
            'parameters': {
                'duration': 1,
                'duration_unit': 't',
                'amount': '1.00',
                'basis': 'stake',
                'symbol': 'R_100'
            }
        }

    def get_info(self):
        """Retorna informações sobre a estratégia"""
        return {
            'name': self.name,
            'tier': self.tier,
            'contract_type': self.contract_type,
            'description': self.description,
            'indicators': f'EMA{self.fast_period} x EMA{self.slow_period}',
            'min_ticks': 30
        }


# Teste da estratégia
if __name__ == "__main__":
    print("=" * 60)
    print("TESTANDO ALPHA BOT 5 - EMA CROSSOVER")
    print("=" * 60)

    bot = AlphaBot5EMA()

    # Simula ticks com mudança de tendência
    np.random.seed(42)
    base_price = 10000
    ticks = [base_price]

    # Primeira metade: tendência de baixa
    for i in range(25):
        change = np.random.randn() * 2 - 1  # Bias negativo
        ticks.append(ticks[-1] + change)

    # Segunda metade: tendência de alta (provoca cruzamento)
    for i in range(25):
        change = np.random.randn() * 2 + 1  # Bias positivo
        ticks.append(ticks[-1] + change)

    # Testa a estratégia
    result = bot.analyze(ticks)

    print(f"\n📊 RESULTADO DA ANÁLISE:")
    print(f"   Sinal: {result['signal'] or 'AGUARDANDO'}")
    print(f"   Confiança: {result['confidence']}%")
    print(f"   Motivo: {result['reason']}")

    if result.get('indicators'):
        print(f"\n📈 INDICADORES:")
        for key, value in result['indicators'].items():
            print(f"   {key}: {value}")

    # Mostra gráfico ASCII das EMAs
    print(f"\n📊 VISUALIZAÇÃO DAS EMAs:")
    print(f"   Preço atual: {result['indicators']['current_price']:.2f}")
    print(f"   EMA {bot.fast_period}:      {result['indicators']['ema_fast']:.2f}")
    print(f"   EMA {bot.slow_period}:      {result['indicators']['ema_slow']:.2f}")

    if result['indicators']['trend'] == 'bullish':
        print(f"   📈 Tendência: ALTA (EMA rápida > EMA lenta)")
    else:
        print(f"   📉 Tendência: BAIXA (EMA rápida < EMA lenta)")

    print(f"\n✅ Estratégia: {bot.get_info()['name']}")
    print(f"   Tipo: {bot.get_info()['tier']}")
    print(f"   Contrato: {bot.get_info()['contract_type']}")