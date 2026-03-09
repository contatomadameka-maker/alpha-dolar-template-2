"""
╔══════════════════════════════════════════════════════════╗
║          ALPHA BOT 2 - MACD CROSSOVER STRATEGY          ║
║                    GRATUITA (FREE)                       ║
╚══════════════════════════════════════════════════════════╝

ESTRATÉGIA:
- Usa MACD (Moving Average Convergence Divergence)
- Identifica cruzamentos da linha MACD com a Signal
- Tipo de contrato: CALL/PUT (Rise/Fall)
- Duração: 1 tick

SINAIS:
- CALL: Quando MACD cruza ACIMA da Signal (tendência de alta)
- PUT: Quando MACD cruza ABAIXO da Signal (tendência de baixa)

INDICADORES:
- MACD (12, 26, 9)
- Confirmação de força do sinal
"""

import pandas as pd
import numpy as np
from datetime import datetime


class AlphaBot2MACD:
    """Alpha Bot 2 - MACD Crossover Strategy"""

    def __init__(self):
        self.name = "Alpha Bot 2 - MACD Crossover"
        self.tier = "FREE"
        self.contract_type = "CALL/PUT"
        self.description = "Estratégia baseada em cruzamentos do MACD"

        # Parâmetros do MACD
        self.fast_period = 12
        self.slow_period = 26
        self.signal_period = 9

        # Histórico de sinais
        self.last_macd = None
        self.last_signal = None

    def calculate_macd(self, prices):
        """
        Calcula o MACD

        Returns:
            tuple: (macd_line, signal_line, histogram)
        """
        df = pd.DataFrame({'close': prices})

        # Calcula EMAs
        ema_fast = df['close'].ewm(span=self.fast_period, adjust=False).mean()
        ema_slow = df['close'].ewm(span=self.slow_period, adjust=False).mean()

        # MACD line
        macd_line = ema_fast - ema_slow

        # Signal line
        signal_line = macd_line.ewm(span=self.signal_period, adjust=False).mean()

        # Histogram
        histogram = macd_line - signal_line

        return macd_line, signal_line, histogram

    def analyze(self, ticks):
        """
        Analisa os ticks e retorna sinal de trade

        Args:
            ticks: Lista de preços recentes (mínimo 50 ticks)

        Returns:
            dict: {
                'signal': 'CALL' ou 'PUT' ou None,
                'contract_type': 'CALL' ou 'PUT',
                'confidence': 0-100,
                'indicators': {...}
            }
        """
        if len(ticks) < 50:
            return {
                'signal': None,
                'reason': 'Aguardando mais dados (mínimo 50 ticks)',
                'confidence': 0
            }

        # Pega apenas os últimos 100 ticks para performance
        recent_ticks = ticks[-100:]
        prices = [float(tick) for tick in recent_ticks]

        # Calcula MACD
        macd_line, signal_line, histogram = self.calculate_macd(prices)

        # Valores atuais
        current_macd = macd_line.iloc[-1]
        current_signal = signal_line.iloc[-1]
        current_histogram = histogram.iloc[-1]

        # Valores anteriores
        prev_macd = macd_line.iloc[-2]
        prev_signal = signal_line.iloc[-2]
        prev_histogram = histogram.iloc[-2]

        # Detecta cruzamento
        signal = None
        confidence = 0
        reason = ""

        # CALL: MACD cruza ACIMA da Signal
        if prev_macd <= prev_signal and current_macd > current_signal:
            signal = "CALL"
            # Confiança baseada na força do histograma
            confidence = min(100, abs(current_histogram) * 1000 + 50)
            reason = f"MACD cruzou acima da Signal (Histograma: {current_histogram:.5f})"

        # PUT: MACD cruza ABAIXO da Signal
        elif prev_macd >= prev_signal and current_macd < current_signal:
            signal = "PUT"
            confidence = min(100, abs(current_histogram) * 1000 + 50)
            reason = f"MACD cruzou abaixo da Signal (Histograma: {current_histogram:.5f})"

        # Sem cruzamento
        else:
            # Verifica se está próximo de um cruzamento
            distance = abs(current_macd - current_signal)
            if distance < 0.0001:
                reason = "MACD e Signal muito próximos - aguardando cruzamento"
            else:
                if current_macd > current_signal:
                    reason = f"MACD acima da Signal - tendência de alta (sem cruzamento recente)"
                else:
                    reason = f"MACD abaixo da Signal - tendência de baixa (sem cruzamento recente)"

        # Atualiza histórico
        self.last_macd = current_macd
        self.last_signal = current_signal

        return {
            'signal': signal,
            'contract_type': signal,  # CALL ou PUT
            'confidence': round(confidence, 2),
            'reason': reason,
            'indicators': {
                'macd': round(current_macd, 5),
                'signal': round(current_signal, 5),
                'histogram': round(current_histogram, 5),
                'prev_macd': round(prev_macd, 5),
                'prev_signal': round(prev_signal, 5)
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
            'indicators': f'MACD({self.fast_period}, {self.slow_period}, {self.signal_period})',
            'min_ticks': 50
        }


# Teste da estratégia
if __name__ == "__main__":
    print("=" * 60)
    print("TESTANDO ALPHA BOT 2 - MACD CROSSOVER")
    print("=" * 60)

    bot = AlphaBot2MACD()

    # Simula ticks
    np.random.seed(42)
    base_price = 10000
    ticks = [base_price]

    # Gera 100 ticks com tendência
    for i in range(100):
        change = np.random.randn() * 5 + 0.1 * np.sin(i / 10)  # Tendência senoidal
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

    print(f"\n✅ Estratégia: {bot.get_info()['name']}")
    print(f"   Tipo: {bot.get_info()['tier']}")
    print(f"   Contrato: {bot.get_info()['contract_type']}")