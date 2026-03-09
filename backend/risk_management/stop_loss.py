"""
Sistema de Stop Loss e Take Profit
Alpha Dolar 2.0
"""
from datetime import datetime

try:
    from ..config import BotConfig
except ImportError:
    from config import BotConfig

class StopLoss:
    """Gerencia limites de perda e ganho"""

    def __init__(self, limite_perda=None, lucro_alvo=None, stop_loss_type=None, max_consecutive_losses=None):
        self.limite_perda = limite_perda or BotConfig.LIMITE_PERDA
        self.lucro_alvo = lucro_alvo or BotConfig.LUCRO_ALVO
        self.stop_loss_type = stop_loss_type or BotConfig.STOP_LOSS_TYPE
        self.max_consecutive_losses = max_consecutive_losses or BotConfig.MAX_CONSECUTIVE_LOSSES

        # Estatísticas
        self.lucro_total = 0.0
        self.perda_total = 0.0
        self.saldo_liquido = 0.0
        self.vitorias = 0
        self.derrotas = 0
        self.perdas_consecutivas = 0
        self.vitorias_consecutivas = 0
        self.max_perdas_consecutivas = 0
        self.max_vitorias_consecutivas = 0

        # Histórico
        self.historico_trades = []
        self.inicio_sessao = datetime.now()

    def registrar_trade(self, profit, vitoria=True):
        """
        Registra resultado de um trade

        Args:
            profit (float): Lucro/prejuízo do trade
            vitoria (bool): True se ganhou, False se perdeu

        Returns:
            dict: Informações do trade registrado
        """
        # Atualiza estatísticas
        if vitoria:
            self.vitorias += 1
            self.lucro_total += abs(profit)
            self.vitorias_consecutivas += 1
            self.perdas_consecutivas = 0

            # Atualiza máximo de vitórias consecutivas
            if self.vitorias_consecutivas > self.max_vitorias_consecutivas:
                self.max_vitorias_consecutivas = self.vitorias_consecutivas
        else:
            self.derrotas += 1
            self.perda_total += abs(profit)
            self.perdas_consecutivas += 1
            self.vitorias_consecutivas = 0

            # Atualiza máximo de perdas consecutivas
            if self.perdas_consecutivas > self.max_perdas_consecutivas:
                self.max_perdas_consecutivas = self.perdas_consecutivas

        # Atualiza saldo líquido
        self.saldo_liquido += profit

        # Adiciona ao histórico
        trade_info = {
            "timestamp": datetime.now(),
            "profit": profit,
            "vitoria": vitoria,
            "saldo_liquido": self.saldo_liquido,
            "perdas_consecutivas": self.perdas_consecutivas,
            "vitorias_consecutivas": self.vitorias_consecutivas
        }
        self.historico_trades.append(trade_info)

        return trade_info

    def deve_parar(self):
        """
        Verifica se deve parar de operar

        Returns:
            tuple: (deve_parar: bool, motivo: str)
        """
        # Verifica lucro alvo
        if self.saldo_liquido >= self.lucro_alvo:
            return True, f"🎯 Lucro alvo atingido! ${self.saldo_liquido:.2f}"

        # Verifica limite de perda por valor
        if self.stop_loss_type == "value":
            if abs(self.saldo_liquido) >= self.limite_perda:
                return True, f"🛑 Limite de perda atingido! ${self.saldo_liquido:.2f}"

        # Verifica limite de perdas consecutivas
        elif self.stop_loss_type == "consecutive_losses":
            if self.perdas_consecutivas >= self.max_consecutive_losses:
                return True, f"🛑 {self.perdas_consecutivas} perdas consecutivas!"

        return False, ""

    def pode_operar(self, saldo_atual):
        """
        Verifica se pode continuar operando

        Args:
            saldo_atual (float): Saldo atual da conta

        Returns:
            tuple: (pode_operar: bool, motivo: str)
        """
        # Verifica saldo mínimo
        if saldo_atual < BotConfig.MIN_BALANCE:
            return False, f"⚠️ Saldo abaixo do mínimo! ${saldo_atual:.2f} < ${BotConfig.MIN_BALANCE:.2f}"

        # Verifica se deve parar por stop loss/take profit
        deve_parar, motivo = self.deve_parar()
        if deve_parar:
            return False, motivo

        return True, "✅ Pode operar"

    def get_win_rate(self):
        """Calcula taxa de acerto"""
        total = self.vitorias + self.derrotas
        if total == 0:
            return 0.0
        return (self.vitorias / total) * 100

    def get_estatisticas(self):
        """Retorna estatísticas completas"""
        total_trades = self.vitorias + self.derrotas
        tempo_sessao = datetime.now() - self.inicio_sessao

        return {
            "saldo_liquido": round(self.saldo_liquido, 2),
            "lucro_total": round(self.lucro_total, 2),
            "perda_total": round(self.perda_total, 2),
            "total_trades": total_trades,
            "vitorias": self.vitorias,
            "derrotas": self.derrotas,
            "win_rate": round(self.get_win_rate(), 2),
            "perdas_consecutivas": self.perdas_consecutivas,
            "vitorias_consecutivas": self.vitorias_consecutivas,
            "max_perdas_consecutivas": self.max_perdas_consecutivas,
            "max_vitorias_consecutivas": self.max_vitorias_consecutivas,
            "tempo_sessao": str(tempo_sessao).split('.')[0],
            "lucro_alvo": self.lucro_alvo,
            "limite_perda": self.limite_perda,
            "distancia_lucro_alvo": round(self.lucro_alvo - self.saldo_liquido, 2),
            "distancia_limite_perda": round(self.limite_perda + self.saldo_liquido, 2)
        }

    def reset(self):
        """Reset completo das estatísticas"""
        self.lucro_total = 0.0
        self.perda_total = 0.0
        self.saldo_liquido = 0.0
        self.vitorias = 0
        self.derrotas = 0
        self.perdas_consecutivas = 0
        self.vitorias_consecutivas = 0
        self.max_perdas_consecutivas = 0
        self.max_vitorias_consecutivas = 0
        self.historico_trades = []
        self.inicio_sessao = datetime.now()

    def reset_diario(self):
        """Reset para novo dia (mantém histórico total)"""
        self.saldo_liquido = 0.0
        self.perdas_consecutivas = 0
        self.vitorias_consecutivas = 0
        self.inicio_sessao = datetime.now()

class TrailingStop:
    """
    Stop Loss Dinâmico (Trailing Stop)
    Move o stop loss conforme o lucro aumenta
    """

    def __init__(self, trailing_distance=None, activation_profit=None):
        self.trailing_distance = trailing_distance or 10.0  # Distância do trailing
        self.activation_profit = activation_profit or 5.0   # Lucro mínimo para ativar

        self.stop_loss_nivel = None
        self.maior_lucro = 0.0
        self.ativado = False

    def atualizar(self, lucro_atual):
        """
        Atualiza nível do trailing stop

        Args:
            lucro_atual (float): Lucro atual

        Returns:
            dict: Informações do trailing stop
        """
        # Ativa trailing se atingiu lucro mínimo
        if not self.ativado and lucro_atual >= self.activation_profit:
            self.ativado = True
            self.stop_loss_nivel = lucro_atual - self.trailing_distance

        # Se ativado, move o stop loss
        if self.ativado:
            if lucro_atual > self.maior_lucro:
                self.maior_lucro = lucro_atual
                self.stop_loss_nivel = lucro_atual - self.trailing_distance

        return {
            "ativado": self.ativado,
            "stop_loss_nivel": self.stop_loss_nivel,
            "maior_lucro": self.maior_lucro,
            "lucro_atual": lucro_atual
        }

    def deve_parar(self, lucro_atual):
        """
        Verifica se trailing stop foi atingido

        Args:
            lucro_atual (float): Lucro atual

        Returns:
            bool: True se deve parar
        """
        if self.ativado and self.stop_loss_nivel is not None:
            return lucro_atual <= self.stop_loss_nivel
        return False

    def reset(self):
        """Reset do trailing stop"""
        self.stop_loss_nivel = None
        self.maior_lucro = 0.0
        self.ativado = False

class SessionManager:
    """Gerencia sessões de trading (diário, semanal, mensal)"""

    def __init__(self):
        self.sessao_diaria = StopLoss()
        self.sessao_semanal = StopLoss()
        self.sessao_mensal = StopLoss()
        self.sessao_total = StopLoss()

        self.ultimo_dia = datetime.now().day
        self.ultima_semana = datetime.now().isocalendar()[1]
        self.ultimo_mes = datetime.now().month

    def registrar_trade(self, profit, vitoria=True):
        """Registra trade em todas as sessões"""
        # Verifica se mudou de dia/semana/mês
        agora = datetime.now()

        if agora.day != self.ultimo_dia:
            self.sessao_diaria.reset_diario()
            self.ultimo_dia = agora.day

        if agora.isocalendar()[1] != self.ultima_semana:
            self.sessao_semanal.reset_diario()
            self.ultima_semana = agora.isocalendar()[1]

        if agora.month != self.ultimo_mes:
            self.sessao_mensal.reset_diario()
            self.ultimo_mes = agora.month

        # Registra em todas as sessões
        self.sessao_diaria.registrar_trade(profit, vitoria)
        self.sessao_semanal.registrar_trade(profit, vitoria)
        self.sessao_mensal.registrar_trade(profit, vitoria)
        self.sessao_total.registrar_trade(profit, vitoria)

    def get_resumo(self):
        """Retorna resumo de todas as sessões"""
        return {
            "hoje": self.sessao_diaria.get_estatisticas(),
            "semana": self.sessao_semanal.get_estatisticas(),
            "mes": self.sessao_mensal.get_estatisticas(),
            "total": self.sessao_total.get_estatisticas()
        }

# ===== TESTE =====
if __name__ == "__main__":
    print("\n" + "="*60)
    print("🛡️ TESTE DE SISTEMA DE STOP LOSS")
    print("="*60 + "\n")

    # Cria stop loss
    stop_loss = StopLoss(limite_perda=50.0, lucro_alvo=100.0)

    # Simula trades
    print("📊 SIMULANDO TRADES:\n")

    trades_simulados = [
        (10.0, True),   # +10
        (15.0, True),   # +15
        (-8.0, False),  # -8
        (-5.0, False),  # -5
        (20.0, True),   # +20
        (25.0, True),   # +25
        (-10.0, False), # -10
        (30.0, True),   # +30
    ]

    for i, (profit, vitoria) in enumerate(trades_simulados, 1):
        stop_loss.registrar_trade(profit, vitoria)
        status = "✅ WIN" if vitoria else "❌ LOSS"
        print(f"Trade {i}: {status:8} | Profit: ${profit:+6.2f} | Líquido: ${stop_loss.saldo_liquido:+7.2f}")

        # Verifica se deve parar
        deve_parar, motivo = stop_loss.deve_parar()
        if deve_parar:
            print(f"\n{motivo}\n")
            break

    # Estatísticas finais
    print("\n" + "="*60)
    print("📈 ESTATÍSTICAS FINAIS:")
    print("="*60)
    stats = stop_loss.get_estatisticas()
    for key, value in stats.items():
        print(f"{key:30} : {value}")

    # Teste Trailing Stop
    print("\n\n" + "="*60)
    print("🔄 TESTE DE TRAILING STOP")
    print("="*60 + "\n")

    trailing = TrailingStop(trailing_distance=5.0, activation_profit=10.0)

    lucros = [5, 8, 12, 15, 18, 20, 18, 16, 14]

    for i, lucro in enumerate(lucros, 1):
        info = trailing.atualizar(lucro)
        deve_parar = trailing.deve_parar(lucro)

        print(f"Step {i}: Lucro=${lucro:5.2f} | Stop=${info['stop_loss_nivel'] if info['stop_loss_nivel'] else 'N/A':6} | Ativado={info['ativado']} | Deve parar={deve_parar}")

        if deve_parar:
            print(f"\n🛑 Trailing Stop ativado! Lucro protegido em ${info['stop_loss_nivel']:.2f}\n")
            break

    print()