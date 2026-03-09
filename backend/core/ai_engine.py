"""
ALPHA DOLAR 2.0 - AI Engine
Motor de Inteligência Artificial para tomada de decisões
"""

import random
from datetime import datetime
from typing import Dict, List, Optional


class AIEngine:
    """Motor de IA para análise e tomada de decisões"""

    def __init__(self, strategy_type="digit_pattern"):
        self.strategy_type = strategy_type
        self.tick_history = []
        self.decision_history = []

        # Estratégias disponíveis
        self.strategies = {
            "digit_pattern": self.analyze_digit_pattern,
            "trend_following": self.analyze_trend,
            "volatility": self.analyze_volatility,
            "smart_random": self.smart_random_decision
        }

    def analyze(self, ticks: List[float], config: Dict) -> Dict:
        """
        Analisa os ticks e retorna decisão de trade

        Args:
            ticks: Lista de preços recentes
            config: Configurações do bot (mercado, tipo, etc)

        Returns:
            dict: {
                'should_trade': bool,
                'contract_type': str,
                'barrier': int (se aplicável),
                'confidence': float,
                'reason': str
            }
        """
        # Atualiza histórico
        self.tick_history.extend(ticks[-10:])
        if len(self.tick_history) > 200:
            self.tick_history = self.tick_history[-200:]

        # Pega estratégia
        strategy_func = self.strategies.get(
            self.strategy_type,
            self.smart_random_decision
        )

        # Analisa
        decision = strategy_func(ticks, config)

        # Registra decisão
        self.decision_history.append({
            'timestamp': datetime.now(),
            'decision': decision,
            'config': config
        })

        return decision

    def analyze_digit_pattern(self, ticks: List[float], config: Dict) -> Dict:
        """Analisa padrões de dígitos"""
        if len(ticks) < 10:
            return {
                'should_trade': False,
                'reason': 'Aguardando mais dados'
            }

        # Extrai últimos dígitos
        digits = [int(str(float(tick)).replace('.', '')[-1]) for tick in ticks[-50:]]

        # Conta frequência
        even_count = sum(1 for d in digits if d % 2 == 0)
        odd_count = len(digits) - even_count

        # Últimos 10 dígitos
        recent_digits = digits[-10:]
        recent_even = sum(1 for d in recent_digits if d % 2 == 0)
        recent_odd = len(recent_digits) - recent_even

        # Decisão baseada em padrão
        contract_type = config.get('contract_type', 'DIGITODD')

        if contract_type == 'DIGITEVEN':
            # Se teve muitos ímpares recentemente, apostar em par
            if recent_odd > 6:
                confidence = min(0.85, 0.5 + (recent_odd - 6) * 0.1)
                return {
                    'should_trade': True,
                    'contract_type': 'DIGITEVEN',
                    'confidence': confidence,
                    'reason': f'Últimos 10: {recent_odd} ímpares, {recent_even} pares. Tendência para par.'
                }

        elif contract_type == 'DIGITODD':
            # Se teve muitos pares recentemente, apostar em ímpar
            if recent_even > 6:
                confidence = min(0.85, 0.5 + (recent_even - 6) * 0.1)
                return {
                    'should_trade': True,
                    'contract_type': 'DIGITODD',
                    'confidence': confidence,
                    'reason': f'Últimos 10: {recent_even} pares, {recent_odd} ímpares. Tendência para ímpar.'
                }

        elif contract_type in ['DIGITOVER', 'DIGITUNDER']:
            # Análise de over/under
            barrier = config.get('barrier', 5)

            over_count = sum(1 for d in recent_digits if d > barrier)
            under_count = sum(1 for d in recent_digits if d < barrier)

            if contract_type == 'DIGITOVER' and under_count > 6:
                return {
                    'should_trade': True,
                    'contract_type': 'DIGITOVER',
                    'barrier': barrier,
                    'confidence': 0.75,
                    'reason': f'Últimos 10: {under_count} abaixo de {barrier}. Correção esperada.'
                }
            elif contract_type == 'DIGITUNDER' and over_count > 6:
                return {
                    'should_trade': True,
                    'contract_type': 'DIGITUNDER',
                    'barrier': barrier,
                    'confidence': 0.75,
                    'reason': f'Últimos 10: {over_count} acima de {barrier}. Correção esperada.'
                }

        # Sem sinal forte
        return {
            'should_trade': False,
            'reason': 'Aguardando padrão mais claro'
        }

    def analyze_trend(self, ticks: List[float], config: Dict) -> Dict:
        """Analisa tendência de preço"""
        if len(ticks) < 10:
            return {
                'should_trade': False,
                'reason': 'Aguardando mais dados'
            }

        recent_ticks = ticks[-10:]

        # Calcula média móvel simples (mais sensível)
        sma_short = sum(recent_ticks[-3:]) / 3
        sma_long = sum(recent_ticks[-7:]) / 7

        current_price = recent_ticks[-1]
        prev_price = recent_ticks[-2]

        contract_type = config.get('contract_type', 'CALL')

        # Detecta movimento
        is_rising = current_price > prev_price
        is_above_sma = current_price > sma_short

        # CALL - Tendência de alta
        if contract_type in ['CALL', 'CALLE']:
            if is_rising and sma_short > sma_long:
                return {
                    'should_trade': True,
                    'contract_type': contract_type,
                    'confidence': 0.72,
                    'reason': 'Preço subindo + SMA curta > SMA longa'
                }
            elif is_rising:
                return {
                    'should_trade': True,
                    'contract_type': contract_type,
                    'confidence': 0.65,
                    'reason': 'Movimento de alta detectado'
                }

        # PUT - Tendência de baixa
        elif contract_type in ['PUT', 'PUTE']:
            if not is_rising and sma_short < sma_long:
                return {
                    'should_trade': True,
                    'contract_type': contract_type,
                    'confidence': 0.72,
                    'reason': 'Preço caindo + SMA curta < SMA longa'
                }
            elif not is_rising:
                return {
                    'should_trade': True,
                    'contract_type': contract_type,
                    'confidence': 0.65,
                    'reason': 'Movimento de baixa detectado'
                }

        return {
            'should_trade': False,
            'reason': 'Aguardando melhor momento'
        }

    def analyze_volatility(self, ticks: List[float], config: Dict) -> Dict:
        """Analisa volatilidade"""
        if len(ticks) < 30:
            return {
                'should_trade': False,
                'reason': 'Aguardando mais dados'
            }

        recent_ticks = ticks[-30:]

        # Calcula desvio padrão
        mean = sum(recent_ticks) / len(recent_ticks)
        variance = sum((x - mean) ** 2 for x in recent_ticks) / len(recent_ticks)
        std_dev = variance ** 0.5

        current_price = recent_ticks[-1]

        # Alta volatilidade = oportunidade
        if std_dev > mean * 0.02:  # 2% de volatilidade
            distance_from_mean = abs(current_price - mean)

            if distance_from_mean > std_dev:
                # Preço muito distante da média = reversão
                if current_price > mean:
                    return {
                        'should_trade': True,
                        'contract_type': 'PUT',
                        'confidence': 0.75,
                        'reason': f'Alta volatilidade. Preço {distance_from_mean:.2f} acima da média.'
                    }
                else:
                    return {
                        'should_trade': True,
                        'contract_type': 'CALL',
                        'confidence': 0.75,
                        'reason': f'Alta volatilidade. Preço {distance_from_mean:.2f} abaixo da média.'
                    }

        return {
            'should_trade': False,
            'reason': 'Volatilidade normal'
        }

    def smart_random_decision(self, ticks: List[float], config: Dict) -> Dict:
        """
        Decisão 'aleatória' inteligente
        Usa probabilidades baseadas em análise básica
        """
        if len(ticks) < 5:
            return {
                'should_trade': False,
                'reason': 'Aguardando dados'
            }

        contract_type = config.get('contract_type', 'DIGITODD')

        # 60% de chance de operar
        if random.random() < 0.6:
            return {
                'should_trade': True,
                'contract_type': contract_type,
                'confidence': random.uniform(0.6, 0.8),
                'reason': 'Análise probabilística favorável'
            }

        return {
            'should_trade': False,
            'reason': 'Aguardando melhor momento'
        }

    def get_statistics(self) -> Dict:
        """Retorna estatísticas das decisões"""
        if not self.decision_history:
            return {
                'total_decisions': 0,
                'trades_executed': 0,
                'avg_confidence': 0
            }

        trades = [d for d in self.decision_history if d['decision'].get('should_trade')]

        total_confidence = sum(
            d['decision'].get('confidence', 0)
            for d in trades
        )

        return {
            'total_decisions': len(self.decision_history),
            'trades_executed': len(trades),
            'trades_skipped': len(self.decision_history) - len(trades),
            'avg_confidence': total_confidence / len(trades) if trades else 0,
            'last_decision': self.decision_history[-1] if self.decision_history else None
        }


if __name__ == "__main__":
    # Teste
    print("=" * 60)
    print("TESTANDO AI ENGINE")
    print("=" * 60)

    engine = AIEngine(strategy_type="digit_pattern")

    # Simula ticks
    ticks = [10000 + random.uniform(-10, 10) for _ in range(50)]

    config = {
        'contract_type': 'DIGITODD',
        'symbol': 'R_100',
        'duration': 1
    }

    # Analisa
    decision = engine.analyze(ticks, config)

    print(f"\n🤖 DECISÃO DA IA:")
    print(f"   Operar: {decision.get('should_trade')}")
    if decision.get('should_trade'):
        print(f"   Tipo: {decision.get('contract_type')}")
        print(f"   Confiança: {decision.get('confidence', 0):.1%}")
    print(f"   Motivo: {decision.get('reason')}")

    # Estatísticas
    stats = engine.get_statistics()
    print(f"\n📊 ESTATÍSTICAS:")
    print(f"   Total de análises: {stats['total_decisions']}")
    print(f"   Trades executados: {stats['trades_executed']}")
    print(f"   Confiança média: {stats['avg_confidence']:.1%}")