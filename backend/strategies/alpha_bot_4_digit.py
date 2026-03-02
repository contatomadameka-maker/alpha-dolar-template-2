"""
╔══════════════════════════════════════════════════════════╗
║       ALPHA BOT 4 - DIGIT PATTERN ANALYSIS              ║
║                    GRATUITA (FREE)                       ║
╚══════════════════════════════════════════════════════════╝
ESTRATÉGIA:
- Analisa frequência e padrões do último dígito dos preços
- Identifica dígitos "frios" (abaixo da frequência esperada)
- Tipo de contrato: DIGITOVER / DIGITUNDER
- Duração: 1 tick

LÓGICA:
- Coleta últimos 100 dígitos (0-9) dos preços
- Calcula frequência de cada dígito
- Encontra barreira ótima com maior desequilíbrio
- Só entra se confiança > 60% e mínimo 50 ticks coletados

FIX 02/03: Integrado com BaseStrategy (should_enter + get_contract_params)
"""
from collections import Counter, deque

try:
    from .base_strategy import BaseStrategy
    from ..config import BotConfig
except ImportError:
    from base_strategy import BaseStrategy
    try:
        from config import BotConfig
    except ImportError:
        class BotConfig:
            DEFAULT_SYMBOL = "R_100"
            BASIS = "stake"


class AlphaBot4DigitPattern(BaseStrategy):
    """Alpha Bot 4 - Digit Pattern Analysis Strategy"""

    def __init__(self):
        super().__init__(name="Alpha Bot 4 - Digit Pattern Analysis")
        self.tier = "FREE"
        self.contract_type = "DIGITOVER/DIGITUNDER"
        self.description = "Análise de padrões do último dígito"

        self.digit_history = deque(maxlen=200)
        self.min_ticks = 50          # mínimo de ticks para operar
        self.min_confidence = 60.0   # confiança mínima para entrar

        self._last_barrier = 5
        self._last_direction = "OVER"

    # ─────────────────────────────────────────
    # HELPERS
    # ─────────────────────────────────────────

    def _get_last_digit(self, price):
        """Extrai o último dígito do preço"""
        price_str = str(float(price)).replace('.', '')
        return int(price_str[-1])

    def _calc_frequency(self, digits):
        """Frequência percentual de cada dígito 0-9"""
        counter = Counter(digits)
        total = len(digits)
        return {d: counter.get(d, 0) / total * 100 for d in range(10)}

    def _find_best_barrier(self, frequency):
        """
        Varre barreiras 1-8 e escolhe a que tem maior vantagem.
        Retorna (barrier, direction, confidence).
        """
        best = None
        for barrier in range(1, 9):
            prob_over  = sum(frequency.get(d, 0) for d in range(barrier + 1, 10))
            prob_under = sum(frequency.get(d, 0) for d in range(0, barrier))

            if prob_over >= prob_under:
                direction, confidence = "OVER", prob_over
            else:
                direction, confidence = "UNDER", prob_under

            if best is None or confidence > best[2]:
                best = (barrier, direction, confidence)

        return best  # (barrier, direction, confidence)

    # ─────────────────────────────────────────
    # INTERFACE BaseStrategy
    # ─────────────────────────────────────────

    def should_enter(self, tick_data):
        """
        Implementação obrigatória da BaseStrategy.
        Retorna (should_enter: bool, direction: str, confidence: float 0-1)
        direction aqui é o contract_type: "DIGITOVER" ou "DIGITUNDER"
        """
        self.update_tick(tick_data)

        price = float(tick_data.get('quote', 0))
        self.digit_history.append(self._get_last_digit(price))

        if len(self.digit_history) < self.min_ticks:
            return False, None, 0.0

        frequency = self._calc_frequency(list(self.digit_history)[-100:])
        barrier, direction, confidence = self._find_best_barrier(frequency)

        self._last_barrier = barrier
        self._last_direction = direction

        if confidence >= self.min_confidence:
            contract = "DIGITOVER" if direction == "OVER" else "DIGITUNDER"
            self.last_signal = contract
            self.signal_count += 1
            return True, contract, round(confidence / 100, 4)

        return False, None, 0.0

    def get_contract_params(self, direction):
        """
        Retorna parâmetros completos do contrato para a API Deriv.
        direction = "DIGITOVER" ou "DIGITUNDER"
        """
        return {
            "contract_type": direction,
            "symbol": BotConfig.DEFAULT_SYMBOL,
            "duration": 1,
            "duration_unit": "t",
            "basis": BotConfig.BASIS,
            "barrier": self._last_barrier
        }

    # ─────────────────────────────────────────
    # INTERFACE analyze() — usada pelo bot.py
    # ─────────────────────────────────────────

    def analyze(self, ticks):
        """
        Recebe lista de preços e retorna dict com sinal.
        Compatível com o bot.py (método analyze).
        """
        if len(ticks) < self.min_ticks:
            return {
                'signal': None,
                'reason': f'Aguardando mais dados ({len(ticks)}/{self.min_ticks} ticks)',
                'confidence': 0
            }

        recent = ticks[-100:] if len(ticks) > 100 else ticks
        digits = [self._get_last_digit(float(t)) for t in recent]
        self.digit_history.extend(digits)

        frequency = self._calc_frequency(digits)
        barrier, direction, confidence = self._find_best_barrier(frequency)

        self._last_barrier = barrier
        self._last_direction = direction

        if confidence >= self.min_confidence:
            contract = "DIGITOVER" if direction == "OVER" else "DIGITUNDER"
            self.last_signal = contract
            self.signal_count += 1

            # Conta dígitos frios para log
            cold_digits = [d for d, f in frequency.items() if f < 8.0]

            return {
                'signal': contract,
                'contract_type': contract,
                'barrier': barrier,
                'confidence': round(confidence, 2),
                'reason': (
                    f"Digit{direction} {barrier} | "
                    f"Confiança: {confidence:.1f}% | "
                    f"Dígitos frios: {cold_digits}"
                ),
                'indicators': {
                    'current_digit': digits[-1],
                    'last_10_digits': digits[-10:],
                    'frequency': {k: round(v, 1) for k, v in frequency.items()},
                    'best_barrier': barrier,
                    'direction': direction,
                    'cold_digits': cold_digits
                },
                'parameters': {
                    'contract_type': contract,
                    'duration': 1,
                    'duration_unit': 't',
                    'symbol': BotConfig.DEFAULT_SYMBOL,
                    'basis': BotConfig.BASIS,
                    'barrier': barrier
                }
            }

        return {
            'signal': None,
            'barrier': barrier,
            'confidence': round(confidence, 2),
            'reason': f'Confiança insuficiente ({confidence:.1f}% < {self.min_confidence}%)'
        }

    def get_info(self):
        return {
            'name': self.name,
            'tier': self.tier,
            'contract_type': self.contract_type,
            'description': self.description,
            'indicators': 'Frequência de dígitos, Barreira ótima, Dígitos frios',
            'min_ticks': self.min_ticks,
            'min_confidence': self.min_confidence
        }

    def reset_state(self):
        """Reset para o watchdog do bot.py"""
        self.digit_history.clear()
        self.last_signal = None
        self.signal_count = 0


# ─────────────────────────────────────────
# TESTE
# ─────────────────────────────────────────
if __name__ == "__main__":
    import random
    print("=" * 60)
    print("TESTANDO ALPHA BOT 4 - DIGIT PATTERN")
    print("=" * 60)

    bot = AlphaBot4DigitPattern()

    # Gera 80 ticks com viés para dígitos altos (6-9)
    random.seed(42)
    ticks = []
    for i in range(80):
        digit = random.choices(
            range(10),
            weights=[5, 5, 5, 5, 8, 8, 15, 15, 17, 17]
        )[0]
        ticks.append(10000.00 + i + digit / 10)

    result = bot.analyze(ticks)

    print(f"\nSinal:      {result.get('signal') or 'AGUARDANDO'}")
    print(f"Barreira:   {result.get('barrier', 'N/A')}")
    print(f"Confiança:  {result.get('confidence')}%")
    print(f"Motivo:     {result.get('reason')}")

    if result.get('indicators'):
        print(f"\nFrequência:")
        for d, f in result['indicators']['frequency'].items():
            bar = '█' * int(f / 4)
            mark = ' ← FRIO' if f < 8 else (' ← QUENTE' if f > 13 else '')
            print(f"  {d}: {f:5.1f}% {bar}{mark}")
        print(f"\nDígitos frios: {result['indicators']['cold_digits']}")
