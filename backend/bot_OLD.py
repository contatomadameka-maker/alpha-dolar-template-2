"""
ALPHA DOLAR 2.0 - Bot de Trading Automatizado
Motor Principal do Bot
ATUALIZADO: Integração com Alpha Bots 2, 4 e 5
"""
import time
import sys
from datetime import datetime
from config import BotConfig, validate_config
from deriv_api import DerivAPI
from risk_management.martingale import Martingale
from risk_management.stop_loss import StopLoss

# ✅ IMPORTAÇÃO DAS NOVAS ESTRATÉGIAS
try:
    from strategies.alpha_bot_2_macd import AlphaBot2MACD
    from strategies.alpha_bot_4_digit import AlphaBot4DigitPattern
    from strategies.alpha_bot_5_ema import AlphaBot5EMA
    STRATEGIES_AVAILABLE = True
except ImportError:
    STRATEGIES_AVAILABLE = False
    print("⚠️ Estratégias Alpha Bot 2, 4, 5 não encontradas!")


class AlphaDolar:
    """Motor principal do bot Alpha Dolar 2.0"""

    def __init__(self, strategy=None, use_martingale=True, bot_number=None):
        self.bot_name = "ALPHA DOLAR 2.0"
        self.version = "2.0.0"

        # API
        self.api = DerivAPI()

        # ✅ SISTEMA DE ESTRATÉGIAS INTELIGENTE
        self.bot_number = bot_number
        self.strategy_manager = StrategyManager()

        # Define estratégia
        if bot_number and STRATEGIES_AVAILABLE:
            # Usa estratégia automática baseada no número do bot
            self.strategy = self.strategy_manager.get_strategy(bot_number)
            if self.strategy is None and strategy is None:
                raise ValueError(f"Alpha Bot {bot_number} não encontrado e nenhuma estratégia alternativa fornecida!")
        elif strategy is None:
            raise ValueError("Estratégia não pode ser None!")
        else:
            self.strategy = strategy

        # Gestão de Risco
        self.martingale = Martingale() if use_martingale else None
        self.stop_loss = StopLoss()

        # Estado
        self.is_running = False
        self.current_stake = BotConfig.STAKE_INICIAL
        self.waiting_contract = False
        self.current_contract_id = None

        # ✅ HISTÓRICO DE TICKS (para estratégias técnicas)
        self.tick_history = []
        self.max_tick_history = 200  # Guarda últimos 200 ticks

        # Estatísticas
        self.trades_hoje = 0
        self.inicio_sessao = datetime.now()

    def print_header(self):
        """Exibe cabeçalho do bot"""
        print("\n" + "="*70)
        print(f"🤖 {self.bot_name} v{self.version}")
        print("="*70)

        # ✅ EXIBE INFO DA ESTRATÉGIA
        strategy_name = getattr(self.strategy, 'name', 'Estratégia Personalizada')
        print(f"📊 Estratégia: {strategy_name}")

        # Se for uma das novas estratégias, mostra detalhes
        if hasattr(self.strategy, 'get_info'):
            info = self.strategy.get_info()
            print(f"   Tipo: {info.get('tier', 'N/A')}")
            print(f"   Contratos: {info.get('contract_type', 'N/A')}")
            print(f"   Indicadores: {info.get('indicators', 'N/A')}")

        print(f"💰 Stake Inicial: ${BotConfig.STAKE_INICIAL}")
        print(f"🎯 Lucro Alvo: ${BotConfig.LUCRO_ALVO}")
        print(f"🛑 Limite Perda: ${BotConfig.LIMITE_PERDA}")
        print(f"⚡ Martingale: {'Ativado' if self.martingale else 'Desativado'}")
        print("="*70 + "\n")

    def log(self, message, level="INFO"):
        """Log formatado"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        emoji = {
            "INFO": "ℹ️",
            "SUCCESS": "✅",
            "ERROR": "❌",
            "WARNING": "⚠️",
            "TRADE": "💰",
            "WIN": "🎉",
            "LOSS": "😞"
        }.get(level, "📝")
        print(f"[{timestamp}] {emoji} {message}")

    def on_tick(self, tick_data):
        """
        Callback chamado quando recebe novo tick
        ✅ ATUALIZADO: Suporta estratégias antigas e novas
        """
        # Se está aguardando resultado de contrato, não faz nada
        if self.waiting_contract:
            return

        # ✅ ADICIONA TICK AO HISTÓRICO
        if 'quote' in tick_data:
            price = float(tick_data['quote'])
            self.tick_history.append(price)

            # Mantém apenas últimos N ticks
            if len(self.tick_history) > self.max_tick_history:
                self.tick_history.pop(0)

        # Verifica se pode operar
        pode_operar, motivo = self.stop_loss.pode_operar(self.api.balance)
        if not pode_operar:
            self.log(motivo, "WARNING")
            self.stop()
            return

        # Verifica limite de trades diários
        if self.trades_hoje >= BotConfig.MAX_TRADES_PER_DAY:
            self.log(f"Limite diário de {BotConfig.MAX_TRADES_PER_DAY} trades atingido!", "WARNING")
            self.stop()
            return

        # ✅ DETECTA TIPO DE ESTRATÉGIA E ANALISA
        signal_data = self.analyze_strategy(tick_data)

        if signal_data and signal_data.get('signal'):
            direction = signal_data['signal']
            confidence = signal_data.get('confidence', 0)

            self.log(f"📊 Sinal detectado: {direction} | Confiança: {confidence:.1f}%", "TRADE")

            # ✅ PASSA OS PARÂMETROS COMPLETOS
            self.executar_trade(direction, signal_data)

    def analyze_strategy(self, tick_data):
        """
        ✅ NOVO: Analisa a estratégia (antiga ou nova)
        Retorna os dados do sinal de forma unificada
        """
        # ✅ ESTRATÉGIAS NOVAS (Alpha Bot 2, 4, 5)
        if hasattr(self.strategy, 'analyze'):
            # Precisa de histórico de ticks
            if len(self.tick_history) < 30:
                return None

            result = self.strategy.analyze(self.tick_history)
            return result

        # ✅ ESTRATÉGIAS ANTIGAS (compatibilidade)
        elif hasattr(self.strategy, 'should_enter'):
            should_enter, direction, confidence = self.strategy.should_enter(tick_data)

            if should_enter and direction:
                return {
                    'signal': direction,
                    'confidence': confidence * 100,  # Converte para porcentagem
                    'contract_type': direction,
                    'parameters': None  # Estratégias antigas não têm parâmetros específicos
                }

        return None

    def executar_trade(self, direction, signal_data=None):
        """
        Executa um trade
        ✅ ATUALIZADO: Suporta parâmetros das novas estratégias
        """
        # Calcula stake atual
        if self.martingale:
            stake = self.martingale.stake_atual
        else:
            stake = self.current_stake

        # Verifica se tem saldo suficiente
        if self.api.balance < stake:
            self.log(f"Saldo insuficiente! Necessário: ${stake:.2f} | Disponível: ${self.api.balance:.2f}", "ERROR")
            return

        # ✅ OBTÉM PARÂMETROS DO CONTRATO
        if signal_data and signal_data.get('parameters'):
            # Nova estratégia com parâmetros completos
            params = signal_data['parameters'].copy()
            params['amount'] = stake  # Sobrescreve o stake
            contract_type = signal_data.get('contract_type', direction)
            barrier = params.get('barrier')
        else:
            # Estratégia antiga - usa método tradicional
            params = self.strategy.get_contract_params(direction)
            contract_type = params.get("contract_type", direction)
            barrier = None

        # Log detalhado
        log_msg = f"🎯 Executando {contract_type} | Stake: ${stake:.2f}"
        if barrier is not None:
            log_msg += f" | Barreira: {barrier}"
        self.log(log_msg, "TRADE")

        # ✅ SOLICITA PROPOSTA (com ou sem barreira)
        proposal_params = {
            'contract_type': contract_type,
            'symbol': params.get("symbol", BotConfig.DEFAULT_SYMBOL),
            'amount': stake,
            'duration': params.get("duration", 1),
            'duration_unit': params.get("duration_unit", "t")
        }

        # Adiciona barreira se necessário
        if barrier is not None:
            proposal_params['barrier'] = barrier

        self.api.get_proposal(**proposal_params)

        # Marca como aguardando
        self.waiting_contract = True
        self.trades_hoje += 1

        # Registra no martingale
        if self.martingale:
            self.martingale.registrar_trade(stake)

    def on_contract_update(self, contract_data):
        """
        Callback chamado quando recebe atualização de contrato
        """
        status = contract_data.get("status")

        # Aguarda finalização
        if status not in ["won", "lost"]:
            return

        # Contrato finalizado
        profit = float(contract_data.get("profit", 0))
        contract_id = contract_data.get("contract_id")

        vitoria = status == "won"

        # Log do resultado
        if vitoria:
            self.log(f"🎉 VITÓRIA! Lucro: ${profit:.2f} | ID: {contract_id}", "WIN")
        else:
            self.log(f"😞 DERROTA! Perda: ${profit:.2f} | ID: {contract_id}", "LOSS")

        # Atualiza martingale
        if self.martingale:
            self.martingale.calcular_proximo_stake(vitoria)
            info = self.martingale.get_info()
            self.log(f"📊 Próximo stake: ${info['stake_atual']:.2f} | Step: {info['step_atual']}/{info['max_steps']}", "INFO")

        # Registra no stop loss
        self.stop_loss.registrar_trade(profit, vitoria)

        # Exibe estatísticas
        stats = self.stop_loss.get_estatisticas()
        self.log(f"📈 Líquido: ${stats['saldo_liquido']:+.2f} | Win Rate: {stats['win_rate']:.1f}% | Trades: {stats['total_trades']}", "INFO")

        # Libera para próximo trade
        self.waiting_contract = False
        self.current_contract_id = None

        # Verifica se deve parar
        deve_parar, motivo = self.stop_loss.deve_parar()
        if deve_parar:
            self.log(motivo, "WARNING")
            self.stop()

    def on_balance_update(self, balance):
        """Callback quando saldo atualiza"""
        self.log(f"💰 Saldo atualizado: ${balance:.2f}", "INFO")

    def start(self):
        """Inicia o bot"""
        try:
            # Valida configuração
            if not validate_config():
                return False

            # Exibe cabeçalho
            self.print_header()

            # Conecta à API
            self.log("Conectando à Deriv API...", "INFO")
            if not self.api.connect():
                self.log("Falha na conexão!", "ERROR")
                return False

            # Autoriza
            self.log("Autorizando...", "INFO")
            if not self.api.authorize():
                self.log("Falha na autorização!", "ERROR")
                return False

            self.log(f"✅ Conectado! Saldo: ${self.api.balance:.2f} {self.api.currency}", "SUCCESS")

            # Verifica saldo mínimo
            if self.api.balance < BotConfig.MIN_BALANCE:
                self.log(f"Saldo insuficiente! Mínimo: ${BotConfig.MIN_BALANCE:.2f}", "ERROR")
                return False

            # Configura callbacks
            self.api.set_tick_callback(self.on_tick)
            self.api.set_contract_callback(self.on_contract_update)
            self.api.set_balance_callback(self.on_balance_update)

            # Inscreve em ticks
            self.api.subscribe_ticks(BotConfig.DEFAULT_SYMBOL)

            # Marca como rodando
            self.is_running = True

            self.log("🚀 Bot iniciado! Aguardando sinais...", "SUCCESS")

            # Loop principal
            while self.is_running:
                time.sleep(1)

            return True

        except KeyboardInterrupt:
            self.log("\n⏹️ Bot interrompido pelo usuário", "WARNING")
            self.stop()
            return True
        except Exception as e:
            self.log(f"Erro fatal: {e}", "ERROR")
            import traceback
            traceback.print_exc()
            return False

    def stop(self):
        """Para o bot"""
        self.is_running = False

        # Exibe relatório final
        self.exibir_relatorio_final()

        # Desconecta
        if self.api:
            self.api.disconnect()

        self.log("Bot encerrado", "INFO")

    def exibir_relatorio_final(self):
        """Exibe relatório final da sessão"""
        print("\n" + "="*70)
        print("📊 RELATÓRIO FINAL DA SESSÃO")
        print("="*70)

        stats = self.stop_loss.get_estatisticas()

        print(f"\n💰 Resultados Financeiros:")
        print(f"   Saldo Líquido: ${stats['saldo_liquido']:+.2f}")
        print(f"   Lucro Total: ${stats['lucro_total']:.2f}")
        print(f"   Perda Total: ${stats['perda_total']:.2f}")

        print(f"\n📈 Estatísticas:")
        print(f"   Total de Trades: {stats['total_trades']}")
        print(f"   Vitórias: {stats['vitorias']}")
        print(f"   Derrotas: {stats['derrotas']}")
        print(f"   Win Rate: {stats['win_rate']:.2f}%")

        print(f"\n🎯 Sequências:")
        print(f"   Vitórias Consecutivas (atual): {stats['vitorias_consecutivas']}")
        print(f"   Perdas Consecutivas (atual): {stats['perdas_consecutivas']}")
        print(f"   Máx. Vitórias Consecutivas: {stats['max_vitorias_consecutivas']}")
        print(f"   Máx. Perdas Consecutivas: {stats['max_perdas_consecutivas']}")

        print(f"\n⏱️ Tempo de Sessão: {stats['tempo_sessao']}")

        if self.martingale:
            print(f"\n🎰 Martingale:")
            info = self.martingale.get_info()
            print(f"   Total Investido: ${info['total_investido']:.2f}")
            print(f"   Ciclos Completos: {info['ciclos_completos']}")

        print("\n" + "="*70 + "\n")


# ✅ NOVO: GERENCIADOR DE ESTRATÉGIAS
class StrategyManager:
    """Gerencia as estratégias disponíveis"""

    def __init__(self):
        self.strategies = {}
        self._load_strategies()

    def _load_strategies(self):
        """Carrega todas as estratégias disponíveis"""
        if not STRATEGIES_AVAILABLE:
            return

        try:
            self.strategies[2] = AlphaBot2MACD()
            self.strategies[4] = AlphaBot4DigitPattern()
            self.strategies[5] = AlphaBot5EMA()
        except Exception as e:
            print(f"⚠️ Erro ao carregar estratégias: {e}")

    def get_strategy(self, bot_number):
        """Retorna estratégia baseada no número do bot"""
        return self.strategies.get(bot_number)

    def list_strategies(self):
        """Lista todas as estratégias disponíveis"""
        return {
            num: strategy.get_info()
            for num, strategy in self.strategies.items()
        }