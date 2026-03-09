"""
ALPHA DOLAR 2.0 - Trade Manager
Gerenciamento de trades, martingale e risk management
"""

from datetime import datetime
from typing import Dict, List, Optional


class TradeManager:
    """Gerencia execução de trades, martingale e estatísticas"""

    def __init__(self, config: Dict):
        """
        Args:
            config: {
                'stake_inicial': float,
                'multiplicador': float,
                'lucro_alvo': float,
                'limite_perda': float,
                'perdas_virtuais': int,
                'modo_virtual': str ('na_perda', 'sempre', 'nunca'),
                'iniciar_com_virtuais': bool
            }
        """
        self.config = config

        # Estado do martingale
        self.stake_atual = config['stake_inicial']
        self.step_martingale = 0
        self.max_steps = 10  # Máximo de passos no martingale

        # Histórico de trades
        self.trades = []

        # Estatísticas
        self.saldo_inicial = 0
        self.saldo_atual = 0
        self.lucro_total = 0
        self.perda_total = 0
        self.vitorias = 0
        self.derrotas = 0
        self.vitorias_consecutivas = 0
        self.derrotas_consecutivas = 0
        self.max_vitorias_consecutivas = 0
        self.max_derrotas_consecutivas = 0

        # Virtual trades
        self.modo_virtual_ativo = config.get('iniciar_com_virtuais', False)
        self.perdas_virtuais_count = 0

        # Controle de risco
        self.atingiu_lucro_alvo = False
        self.atingiu_limite_perda = False

    def set_saldo_inicial(self, saldo: float):
        """Define saldo inicial"""
        self.saldo_inicial = saldo
        self.saldo_atual = saldo

    def pode_operar(self) -> tuple[bool, str]:
        """
        Verifica se pode executar novo trade

        Returns:
            (pode_operar, motivo)
        """
        # Verifica lucro alvo
        if self.lucro_total >= self.config['lucro_alvo']:
            self.atingiu_lucro_alvo = True
            return False, f"✅ Lucro alvo de ${self.config['lucro_alvo']:.2f} atingido!"

        # Verifica limite de perda
        if abs(self.lucro_total) >= self.config['limite_perda']:
            self.atingiu_limite_perda = True
            return False, f"🛑 Limite de perda de ${self.config['limite_perda']:.2f} atingido!"

        # Verifica saldo suficiente
        if self.saldo_atual < self.stake_atual:
            return False, f"❌ Saldo insuficiente! Necessário: ${self.stake_atual:.2f}"

        return True, "OK"

    def preparar_trade(self, decision: Dict) -> Optional[Dict]:
        """
        Prepara parâmetros do trade

        Args:
            decision: Decisão da IA

        Returns:
            Parâmetros do trade ou None se não deve operar
        """
        # Verifica se pode operar
        pode, motivo = self.pode_operar()
        if not pode:
            return None

        # Verifica se deve operar (decisão da IA)
        if not decision.get('should_trade'):
            return None

        # Prepara parâmetros
        params = {
            'contract_type': decision['contract_type'],
            'amount': self.stake_atual,
            'basis': 'stake',
            'currency': 'USD',
            'duration': self.config.get('duration', 1),
            'duration_unit': self.config.get('duration_unit', 't'),
            'symbol': self.config.get('symbol', 'R_100'),
            'is_virtual': self.modo_virtual_ativo
        }

        # Adiciona barreira se necessário
        if 'barrier' in decision:
            params['barrier'] = decision['barrier']

        return params

    def registrar_trade(self, params: Dict, resultado: Dict):
        """
        Registra resultado de um trade

        Args:
            params: Parâmetros do trade executado
            resultado: {
                'status': 'won' ou 'lost',
                'profit': float,
                'contract_id': str
            }
        """
        vitoria = resultado['status'] == 'won'
        profit = float(resultado.get('profit', 0))

        # Registra no histórico
        trade_record = {
            'timestamp': datetime.now(),
            'params': params,
            'resultado': resultado,
            'vitoria': vitoria,
            'profit': profit,
            'stake': params['amount'],
            'step_martingale': self.step_martingale,
            'is_virtual': params.get('is_virtual', False)
        }

        self.trades.append(trade_record)

        # Atualiza estatísticas (apenas trades reais)
        if not params.get('is_virtual'):
            self.saldo_atual += profit

            if vitoria:
                self.lucro_total += profit
                self.vitorias += 1
                self.vitorias_consecutivas += 1
                self.derrotas_consecutivas = 0

                if self.vitorias_consecutivas > self.max_vitorias_consecutivas:
                    self.max_vitorias_consecutivas = self.vitorias_consecutivas

                # Reseta martingale
                self.stake_atual = self.config['stake_inicial']
                self.step_martingale = 0

                # Verifica modo virtual
                if self.modo_virtual_ativo:
                    self.modo_virtual_ativo = False

            else:
                self.perda_total += abs(profit)
                self.derrotas += 1
                self.derrotas_consecutivas += 1
                self.vitorias_consecutivas = 0

                if self.derrotas_consecutivas > self.max_derrotas_consecutivas:
                    self.max_derrotas_consecutivas = self.derrotas_consecutivas

                # Aplica martingale
                self.aplicar_martingale()

        # Gerenciamento de trades virtuais
        else:
            if not vitoria:
                self.perdas_virtuais_count += 1

                # Verifica se deve voltar para real
                modo_virtual = self.config.get('modo_virtual', 'na_perda')
                perdas_virtuais_config = self.config.get('perdas_virtuais', 0)

                if modo_virtual == 'na_perda' and self.perdas_virtuais_count >= perdas_virtuais_config:
                    self.modo_virtual_ativo = False
                    self.perdas_virtuais_count = 0
            else:
                # Vitória virtual = continua virtual
                pass

    def aplicar_martingale(self):
        """Aplica martingale após derrota"""
        if self.step_martingale < self.max_steps:
            multiplicador = self.config.get('multiplicador', 2.2)
            self.stake_atual *= multiplicador
            self.step_martingale += 1
        else:
            # Atingiu máximo de steps, reseta
            self.stake_atual = self.config['stake_inicial']
            self.step_martingale = 0

    def get_estatisticas(self) -> Dict:
        """Retorna estatísticas completas"""
        total_trades = self.vitorias + self.derrotas
        win_rate = (self.vitorias / total_trades * 100) if total_trades > 0 else 0

        lucro_liquido = self.lucro_total - self.perda_total
        roi = (lucro_liquido / self.saldo_inicial * 100) if self.saldo_inicial > 0 else 0

        return {
            'saldo_inicial': self.saldo_inicial,
            'saldo_atual': self.saldo_atual,
            'lucro_total': self.lucro_total,
            'perda_total': self.perda_total,
            'lucro_liquido': lucro_liquido,
            'roi': roi,
            'total_trades': total_trades,
            'vitorias': self.vitorias,
            'derrotas': self.derrotas,
            'win_rate': win_rate,
            'vitorias_consecutivas': self.vitorias_consecutivas,
            'derrotas_consecutivas': self.derrotas_consecutivas,
            'max_vitorias_consecutivas': self.max_vitorias_consecutivas,
            'max_derrotas_consecutivas': self.max_derrotas_consecutivas,
            'stake_atual': self.stake_atual,
            'step_martingale': self.step_martingale,
            'modo_virtual_ativo': self.modo_virtual_ativo,
            'atingiu_lucro_alvo': self.atingiu_lucro_alvo,
            'atingiu_limite_perda': self.atingiu_limite_perda,
            'progresso_lucro': (self.lucro_total / self.config['lucro_alvo'] * 100) if self.config['lucro_alvo'] > 0 else 0
        }

    def get_historico_recente(self, limit: int = 10) -> List[Dict]:
        """Retorna últimos N trades"""
        return self.trades[-limit:] if self.trades else []

    def exportar_historico(self, formato: str = 'dict') -> List[Dict]:
        """Exporta histórico completo"""
        if formato == 'dict':
            return self.trades
        elif formato == 'csv':
            # Converte para formato CSV
            csv_data = []
            for trade in self.trades:
                csv_data.append({
                    'timestamp': trade['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
                    'symbol': trade['params']['symbol'],
                    'contract_type': trade['params']['contract_type'],
                    'stake': trade['stake'],
                    'resultado': 'VITÓRIA' if trade['vitoria'] else 'DERROTA',
                    'profit': trade['profit'],
                    'is_virtual': 'SIM' if trade['is_virtual'] else 'NÃO'
                })
            return csv_data

        return self.trades


if __name__ == "__main__":
    # Teste
    print("=" * 60)
    print("TESTANDO TRADE MANAGER")
    print("=" * 60)

    config = {
        'stake_inicial': 1.0,
        'multiplicador': 2.2,
        'lucro_alvo': 20.0,
        'limite_perda': 50.0,
        'perdas_virtuais': 2,
        'modo_virtual': 'na_perda',
        'iniciar_com_virtuais': True,
        'duration': 1,
        'duration_unit': 't',
        'symbol': 'R_100'
    }

    manager = TradeManager(config)
    manager.set_saldo_inicial(100.0)

    # Simula alguns trades
    print("\n🎮 SIMULANDO TRADES...\n")

    # Trade 1 - Virtual Loss
    decision1 = {'should_trade': True, 'contract_type': 'DIGITODD', 'confidence': 0.75}
    params1 = manager.preparar_trade(decision1)
    print(f"Trade 1 (Virtual): Stake ${params1['amount']:.2f}")
    manager.registrar_trade(params1, {'status': 'lost', 'profit': -params1['amount']})

    # Trade 2 - Virtual Loss
    decision2 = {'should_trade': True, 'contract_type': 'DIGITODD', 'confidence': 0.75}
    params2 = manager.preparar_trade(decision2)
    print(f"Trade 2 (Virtual): Stake ${params2['amount']:.2f}")
    manager.registrar_trade(params2, {'status': 'lost', 'profit': -params2['amount']})

    # Trade 3 - Real Win
    decision3 = {'should_trade': True, 'contract_type': 'DIGITODD', 'confidence': 0.75}
    params3 = manager.preparar_trade(decision3)
    print(f"Trade 3 (Real): Stake ${params3['amount']:.2f}")
    manager.registrar_trade(params3, {'status': 'won', 'profit': params3['amount'] * 0.95})

    # Estatísticas
    stats = manager.get_estatisticas()
    print(f"\n📊 ESTATÍSTICAS:")
    print(f"   Saldo: ${stats['saldo_atual']:.2f}")
    print(f"   Lucro Líquido: ${stats['lucro_liquido']:.2f}")
    print(f"   Win Rate: {stats['win_rate']:.1f}%")
    print(f"   Trades: {stats['total_trades']} (V:{stats['vitorias']} D:{stats['derrotas']})")
    print(f"   Próximo stake: ${stats['stake_atual']:.2f}")
    print(f"   Modo virtual: {'SIM' if stats['modo_virtual_ativo'] else 'NÃO'}")