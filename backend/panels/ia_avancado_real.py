"""
ALPHA DOLAR 2.0 - IA AVANÇADO COM API REAL + MACHINE LEARNING
Versão final integrada com Deriv API e ML
MELHOR QUE DC BOTS!
"""

import sys
import os
import time
import asyncio
from datetime import datetime
from threading import Thread

# Adiciona o diretório pai ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from markets import (
    get_all_markets,
    get_markets_by_category,
    MARKET_CATEGORIES,
    get_all_contract_types,
    get_contracts_by_category,
    CONTRACT_CATEGORIES
)

from core import AIEngine, TradeManager

# Importa config
try:
    from config_deriv import DERIV_CONFIG, OPERATION_MODES, get_deriv_token
except:
    DERIV_CONFIG = {'demo': {'token': 'Tr0TSI8LBd11lfS'}}
    OPERATION_MODES = {
        'simulado': {'name': '🎮 Simulado', 'use_real_api': False},
        'demo': {'name': '🧪 Demo', 'use_real_api': True, 'account_type': 'demo'},
        'real': {'name': '💰 Real', 'use_real_api': True, 'account_type': 'real'}
    }

# Tenta importar ML
ML_AVAILABLE = False
try:
    from ml import MLPredictor, prepare_features
    from pathlib import Path
    ML_AVAILABLE = True
except ImportError:
    pass


class IAAvancadoReal:
    """Bot IA Avançado com integração API Real + Machine Learning"""

    def __init__(self):
        self.name = "ALPHA DOLAR 2.0 - IA AVANÇADO + API REAL + ML"
        self.version = "2.0.1"

        # Modo de operação
        self.operation_mode = 'simulado'  # simulado, demo, real

        # Configurações
        self.config = {
            'symbol': 'R_100',
            'market_name': 'Volatility 100 Index',
            'contract_type': 'DIGITODD',
            'contract_name': 'Ímpar',
            'duration': 1,
            'duration_unit': 't',
            'stake_inicial': 1.0,
            'multiplicador': 2.2,
            'lucro_alvo': 20.0,
            'limite_perda': 1000.0,
            'perdas_virtuais': 0,
            'modo_virtual': 'nunca',
            'iniciar_com_virtuais': False,
            'barrier': None,
            'modo_operacao': 'balanceado',
            'confianca_minima': 0.55,
            'use_ml': True  # 🆕 Usar ML se disponível
        }

        # Modos de velocidade
        self.modos = {
            'baixo_risco': {
                'name': '🛡️ Baixo Risco',
                'desc': 'Máxima precisão, menos negociações',
                'confianca': 0.70,
                'intervalo': 5,
                'premium': True
            },
            'preciso': {
                'name': '🎯 Preciso',
                'desc': 'Menos negociações, mais precisão',
                'confianca': 0.65,
                'intervalo': 4,
                'premium': False
            },
            'balanceado': {
                'name': '⚖️ Balanceado',
                'desc': 'Negociações e precisão balanceada',
                'confianca': 0.55,
                'intervalo': 3,
                'premium': False
            },
            'veloz': {
                'name': '⚡ Veloz',
                'desc': 'Mais negociações, menos precisão',
                'confianca': 0.45,
                'intervalo': 2,
                'premium': False
            }
        }

        # Componentes
        self.ai_engine = None
        self.trade_manager = None
        self.deriv_bridge = None
        self.is_running = False

        # ML
        self.ml_predictor = None
        self.ml_enabled = False

        # Async loop
        self.loop = None
        self.loop_thread = None

        # Saldo
        self.saldo_inicial = 10000.0

        # 🆕 Inicializa ML
        self.init_ml()

    def init_ml(self):
        """Inicializa Machine Learning se disponível"""
        if not ML_AVAILABLE:
            return

        try:
            model_path = Path('models/rf_predictor.pkl')

            if model_path.exists():
                self.ml_predictor = MLPredictor()
                self.ml_predictor.load(str(model_path))
                self.ml_enabled = True

                print("\n🧠 ═══════════════════════════════════════════════════")
                print("   MACHINE LEARNING ATIVADO!")
                print("═══════════════════════════════════════════════════")
                print(f"✅ Modelo: {self.ml_predictor.model_type}")
                print(f"✅ Acurácia: {self.ml_predictor.accuracy:.2%}")
                print(f"✅ Treinado em: {self.ml_predictor.training_date}")
                print("═══════════════════════════════════════════════════\n")
            else:
                print("\n⚠️  Machine Learning não disponível")
                print("   Para ativar ML:")
                print("   1. pip install scikit-learn xgboost --break-system-packages")
                print("   2. python3 scripts/train_ml.py\n")

        except Exception as e:
            print(f"⚠️ Erro ao carregar ML: {e}")

    def print_header(self):
        """Cabeçalho"""
        print("\n" + "=" * 70)
        print(f"🤖 {self.name} v{self.version}")
        print("=" * 70)
        print("💡 Sistema com IA + API Real + Machine Learning")
        print("📊 Melhor que DC Bots - Mais mercados, mais contratos!")
        if self.ml_enabled:
            print("🧠 ML ATIVO - Acurácia: {:.1f}%".format(self.ml_predictor.accuracy * 100))
        print("=" * 70 + "\n")

    def print_box(self, title, content, color="blue"):
        """Caixa bonita"""
        emojis = {"blue": "💙", "green": "💚", "red": "❤️", "yellow": "💛"}

        print(f"\n{emojis.get(color, '💙')} ╔{'═' * 66}╗")
        print(f"  ║ {title:^64} ║")
        print(f"  ╠{'═' * 66}╣")
        for line in content:
            print(f"  ║ {line:64} ║")
        print(f"  ╚{'═' * 66}╝\n")

    def selecionar_modo_operacao(self):
        """Seleciona modo de operação (Simulado/Demo/Real)"""
        print("\n" + "=" * 70)
        print("🎮 MODO DE OPERAÇÃO")
        print("=" * 70)

        modes = [
            ('simulado', '🎮 Simulado', 'Ticks e trades simulados (sem API)', False),
            ('demo', '🧪 Demo', 'API Real + Conta Demo ($10k virtual)', False),
            ('real', '💰 Real', 'API Real + DINHEIRO REAL ⚠️', True)
        ]

        for idx, (key, name, desc, warning) in enumerate(modes, 1):
            atual = " ← ATUAL" if key == self.operation_mode else ""
            aviso = " ⚠️ CUIDADO!" if warning else ""
            print(f"{idx}. {name}{aviso}{atual}")
            print(f"    💡 {desc}")

        print("0. ⬅️ Voltar")

        try:
            choice = int(input("\n👉 Escolha o modo: ") or "0")

            if choice == 0:
                return

            if 1 <= choice <= len(modes):
                mode_key = modes[choice - 1][0]

                # Confirma se for modo real
                if mode_key == 'real':
                    print("\n⚠️⚠️⚠️ ATENÇÃO! MODO REAL USA DINHEIRO DE VERDADE! ⚠️⚠️⚠️")
                    confirma = input("Tem certeza? Digite 'CONFIRMO': ")
                    if confirma != 'CONFIRMO':
                        print("❌ Cancelado. Modo não alterado.")
                        return

                self.operation_mode = mode_key
                mode_name = modes[choice - 1][1]
                print(f"\n✅ Modo selecionado: {mode_name}")

        except (ValueError, IndexError):
            print("❌ Opção inválida!")

    def configurar_modo_velocidade(self):
        """Configura modo de velocidade"""
        print("\n" + "=" * 70)
        print("⚡ MODO DE VELOCIDADE")
        print("=" * 70)

        for idx, (key, modo) in enumerate(self.modos.items(), 1):
            premium = " 👑 PREMIUM" if modo['premium'] else ""
            atual = " ← ATUAL" if key == self.config['modo_operacao'] else ""
            print(f"{idx}. {modo['name']}{premium}{atual}")
            print(f"    💡 {modo['desc']}")
            print(f"    📊 Confiança mínima: {modo['confianca']:.0%}")

        print("0. ⬅️ Voltar")

        try:
            choice = int(input("\n👉 Escolha o modo: ") or "0")

            if choice == 0:
                return

            modos_list = list(self.modos.keys())
            if 1 <= choice <= len(modos_list):
                modo_key = modos_list[choice - 1]
                modo = self.modos[modo_key]

                if modo['premium']:
                    print("\n⚠️ Este modo é PREMIUM!")
                    confirma = input("Você tem acesso premium? (s/n): ")
                    if confirma.lower() != 's':
                        print("❌ Modo não disponível.")
                        return

                self.config['modo_operacao'] = modo_key
                self.config['confianca_minima'] = modo['confianca']
                print(f"\n✅ Modo: {modo['name']}")

        except (ValueError, IndexError):
            print("❌ Opção inválida!")

    def configurar_mercado(self):
        """Seleciona mercado"""
        print("\n" + "=" * 70)
        print("📊 SELECIONAR MERCADO")
        print("=" * 70)

        principais = [
            ("volatility_continuous", "📊 Índices de Volatilidade"),
            ("crash_boom", "💥 Crash/Boom"),
            ("volatility_jump", "🦘 Jump Indices")
        ]

        for idx, (key, name) in enumerate(principais, 1):
            markets = get_markets_by_category(key)
            print(f"{idx}. {name} ({len(markets)} mercados)")

        print("0. ⬅️ Manter atual")

        try:
            choice = int(input(f"\n👉 Escolha (atual: {self.config['market_name']}): ") or "0")

            if choice == 0:
                return

            if 1 <= choice <= len(principais):
                key, _ = principais[choice - 1]
                markets = get_markets_by_category(key)

                print(f"\n{MARKET_CATEGORIES[choice - 1]['icon']} {MARKET_CATEGORIES[choice - 1]['name']}")
                print("=" * 70)

                for idx, market in enumerate(markets, 1):
                    print(f"{idx}. {market['icon']} {market['name']}")

                m_choice = int(input("\n👉 Escolha um mercado: "))

                if 1 <= m_choice <= len(markets):
                    market = markets[m_choice - 1]
                    self.config['symbol'] = market['symbol']
                    self.config['market_name'] = market['name']
                    print(f"✅ Mercado: {market['icon']} {market['name']}")

        except (ValueError, IndexError):
            print("❌ Opção inválida!")

    def configurar_tipo_contrato(self):
        """Seleciona tipo de contrato"""
        print("\n" + "=" * 70)
        print("🎯 TIPO DE NEGOCIAÇÃO")
        print("=" * 70)

        populares = [
            ("DIGITODD", "🔴 Ímpar"),
            ("DIGITEVEN", "🔵 Par"),
            ("CALL", "⬆️ Rise"),
            ("PUT", "⬇️ Fall"),
        ]

        for idx, (tipo, nome) in enumerate(populares, 1):
            print(f"{idx}. {nome}")

        print("0. ⬅️ Manter atual")

        try:
            choice = int(input(f"\n👉 Escolha (atual: {self.config['contract_name']}): ") or "0")

            if choice == 0:
                return

            if 1 <= choice <= len(populares):
                tipo, nome = populares[choice - 1]
                self.config['contract_type'] = tipo
                self.config['contract_name'] = nome
                self.config['barrier'] = None
                print(f"✅ Tipo: {nome}")

        except (ValueError, IndexError):
            print("❌ Opção inválida!")

    def configurar_parametros(self):
        """Configura parâmetros"""
        print("\n" + "=" * 70)
        print("⚙️ PARÂMETROS DE TRADING")
        print("=" * 70)

        print(f"\n💰 Quantia Inicial (atual: ${self.config['stake_inicial']:.2f})")
        stake = input("👉 Digite o valor: $") or str(self.config['stake_inicial'])
        self.config['stake_inicial'] = float(stake)

        print(f"\n📈 Multiplicador Martingale (atual: {self.config['multiplicador']:.1f}x)")
        mult = input("👉 Digite o multiplicador: ") or str(self.config['multiplicador'])
        self.config['multiplicador'] = float(mult)

        print(f"\n🎯 Lucro Alvo (atual: ${self.config['lucro_alvo']:.2f})")
        lucro = input("👉 Digite o valor: $") or str(self.config['lucro_alvo'])
        self.config['lucro_alvo'] = float(lucro)

        print(f"\n🛑 Limite de Perda (atual: ${self.config['limite_perda']:.2f})")
        perda = input("👉 Digite o valor: $") or str(self.config['limite_perda'])
        self.config['limite_perda'] = float(perda)

        print("\n✅ Parâmetros configurados!")

    def mostrar_configuracao(self):
        """Mostra configuração"""
        stats = self.trade_manager.get_estatisticas() if self.trade_manager else None

        lucro_display = f"${stats['lucro_liquido']:+.2f} ({stats['roi']:+.1f}%)" if stats else "$0.00 (0%)"

        # Modo de operação
        mode_info = OPERATION_MODES.get(self.operation_mode, {})
        mode_name = mode_info.get('name', '🎮 Simulado')

        # Modo de velocidade
        modo_vel = self.modos.get(self.config['modo_operacao'], self.modos['balanceado'])

        # Saldo
        if self.deriv_bridge:
            saldo = self.deriv_bridge.get_balance()
        else:
            saldo = self.saldo_inicial

        # ML status
        ml_status = "🧠 ML ATIVO" if self.ml_enabled else "🎲 Estratégias"

        content = [
            f"💰 Lucro: {lucro_display}  |  Saldo: ${saldo:.2f}",
            "",
            f"🎮 Modo: {mode_name}  |  {ml_status}",
            f"⚡ Velocidade: {modo_vel['name']}",
            f"📊 Mercado: {self.config['market_name']}",
            f"🎯 Tipo: {self.config['contract_name']}",
            "",
            f"💵 Stake: ${self.config['stake_inicial']:.2f}  |  Mult: {self.config['multiplicador']:.1f}x",
            f"🎯 Alvo: ${self.config['lucro_alvo']:.2f}  |  Stop: ${self.config['limite_perda']:.2f}",
            ""
        ]

        if stats:
            content.extend([
                f"📊 Trades: {stats['total_trades']} (V:{stats['vitorias']} D:{stats['derrotas']})",
                f"📈 Win Rate: {stats['win_rate']:.1f}%  |  Próximo: ${stats['stake_atual']:.2f}"
            ])

        self.print_box("CONFIGURAÇÕES - IA AVANÇADO + API + ML", content, "blue")

    def analise_ml(self, ticks):
        """🆕 Análise usando Machine Learning"""
        if not self.ml_enabled or not self.ml_predictor:
            return None

        try:
            # Prepara features
            features = prepare_features(ticks, window_size=10)

            if features is None:
                return None

            # Prediz
            prediction, confidence = self.ml_predictor.predict_even_odd(features)

            if prediction is None:
                return None

            # Verifica se predição bate com tipo configurado
            contract_type = self.config['contract_type']
            should_trade = False

            if contract_type == 'DIGITEVEN' and prediction == 'EVEN':
                should_trade = True
            elif contract_type == 'DIGITODD' and prediction == 'ODD':
                should_trade = True

            return {
                'should_trade': should_trade,
                'contract_type': contract_type,
                'confidence': confidence,
                'reason': f'🧠 ML prediz: {prediction} ({confidence:.1%})'
            }

        except Exception as e:
            return None

    def analise_veloz(self, ticks):
        """Análise veloz (fallback)"""
        import random

        if len(ticks) < 5:
            return {'should_trade': False, 'reason': 'Aguardando ticks'}

        contract_type = self.config['contract_type']
        digits = [int(str(float(t)).replace('.', '')[-1]) for t in ticks[-5:]]
        even = sum(1 for d in digits if d % 2 == 0)
        odd = len(digits) - even

        if contract_type == 'DIGITEVEN':
            if odd >= 3 or random.random() < 0.6:
                return {
                    'should_trade': True,
                    'contract_type': 'DIGITEVEN',
                    'confidence': 0.50 + random.uniform(0, 0.15),
                    'reason': f'🎲 Padrão: {odd} ímpares'
                }
        elif contract_type == 'DIGITODD':
            if even >= 3 or random.random() < 0.6:
                return {
                    'should_trade': True,
                    'contract_type': 'DIGITODD',
                    'confidence': 0.50 + random.uniform(0, 0.15),
                    'reason': f'🎲 Padrão: {even} pares'
                }

        return {'should_trade': False, 'reason': 'Aguardando'}

    async def iniciar_robo_async(self):
        """Inicia robô (versão async)"""
        # Seleciona estratégia
        contract_type = self.config['contract_type']

        if contract_type in ['DIGITODD', 'DIGITEVEN', 'DIGITOVER', 'DIGITUNDER']:
            strategy = "digit_pattern"
            strategy_name = "Análise de Padrões de Dígitos"
        elif contract_type in ['CALL', 'PUT']:
            strategy = "trend_following"
            strategy_name = "Seguimento de Tendência"
        else:
            strategy = "smart_random"
            strategy_name = "Análise Probabilística"

        # Mostra estratégia
        if self.ml_enabled and self.config.get('use_ml', True):
            print("🧠 Estratégia Principal: MACHINE LEARNING")
            print(f"🎲 Fallback: {strategy_name}")
        else:
            print(f"🧠 Estratégia: {strategy_name}")

        # Inicializa componentes
        self.ai_engine = AIEngine(strategy_type=strategy)
        self.trade_manager = TradeManager(self.config)

        # Importa e cria bridge
        try:
            from api.deriv_bridge import create_bridge

            # Token baseado no modo
            if self.operation_mode == 'demo':
                token = DERIV_CONFIG.get('demo', {}).get('token')
            elif self.operation_mode == 'real':
                token = DERIV_CONFIG.get('real', {}).get('token')
            else:
                token = None

            self.deriv_bridge = create_bridge(mode=self.operation_mode, token=token)
            await self.deriv_bridge.connect()

            # Saldo inicial
            saldo = self.deriv_bridge.get_balance()
            self.trade_manager.set_saldo_inicial(saldo)

        except Exception as e:
            print(f"⚠️ Erro ao conectar API: {e}")
            print("🎮 Continuando em modo simulado...")
            self.operation_mode = 'simulado'
            self.trade_manager.set_saldo_inicial(self.saldo_inicial)

        self.is_running = True

        print("\n" + "=" * 70)
        print("🚀 ROBÔ INICIADO!")
        print("=" * 70)
        print("💡 Pressione Ctrl+C para pausar")
        print("=" * 70 + "\n")

        # Info do modo
        modo_config = self.modos.get(self.config['modo_operacao'], self.modos['balanceado'])
        intervalo_analise = modo_config['intervalo']

        print(f"🎮 Modo Operação: {OPERATION_MODES[self.operation_mode]['name']}")
        print(f"⚡ Modo Velocidade: {modo_config['name']}")
        print(f"📊 Analisando a cada {intervalo_analise} ticks")
        print(f"🎯 Confiança mínima: {modo_config['confianca']:.0%}")
        if self.ml_enabled:
            print(f"🧠 ML: ATIVADO (Acurácia: {self.ml_predictor.accuracy:.1%})")
        print()

        tick_count = 0
        ticks_buffer = []

        # Callback para ticks
        def on_tick(price):
            nonlocal tick_count
            ticks_buffer.append(price)
            tick_count += 1

        # Subscreve ticks
        if self.deriv_bridge:
            await self.deriv_bridge.subscribe_ticks(self.config['symbol'], on_tick)

        try:
            while self.is_running:
                # Gera tick se simulado
                if self.operation_mode == 'simulado' and self.deriv_bridge:
                    self.deriv_bridge.generate_sim_tick()

                # Mantém buffer
                if len(ticks_buffer) > 100:
                    ticks_buffer = ticks_buffer[-100:]

                # Analisa
                if tick_count % intervalo_analise == 0 and len(ticks_buffer) >= 10:
                    await self.processar_trade(ticks_buffer)

                # Status
                if tick_count % 10 == 0:
                    self.mostrar_status_linha()

                # Aguarda
                await asyncio.sleep(1)

        except KeyboardInterrupt:
            print("\n\n⏸️ Robô pausado!")
        finally:
            self.is_running = False
            if self.deriv_bridge:
                await self.deriv_bridge.disconnect()

    async def processar_trade(self, ticks):
        """🆕 Processa trade (ML + Fallback)"""
        decision = None

        # Tenta ML primeiro
        if self.ml_enabled and self.config.get('use_ml', True):
            decision = self.analise_ml(ticks)

        # Se ML não decidiu, usa estratégias
        if decision is None or not decision.get('should_trade'):
            if self.config['modo_operacao'] == 'veloz':
                decision = self.analise_veloz(ticks)
            else:
                decision = self.ai_engine.analyze(ticks, self.config)

        # Filtra confiança
        confianca_minima = self.config['confianca_minima']
        confidence = decision.get('confidence', 0)

        if decision.get('should_trade') and confidence < confianca_minima:
            decision['should_trade'] = False

        # Prepara trade
        params = self.trade_manager.preparar_trade(decision)

        if params and self.deriv_bridge:
            print(f"\n🎯 EXECUTANDO TRADE:")
            print(f"   Tipo: {params['contract_type']}")
            print(f"   Stake: ${params['amount']:.2f}")
            print(f"   Modo: {OPERATION_MODES[self.operation_mode]['name']}")
            if decision.get('reason'):
                print(f"   {decision['reason']}")

            # Executa
            result = await self.deriv_bridge.execute_trade(params)

            if result:
                emoji = "🎉" if result['status'] == 'won' else "😞"
                print(f"   {emoji} {result['status'].upper()}: ${result['profit']:+.2f}")

                # Registra
                self.trade_manager.registrar_trade(params, result)

    def mostrar_status_linha(self):
        """Status em uma linha"""
        if not self.trade_manager:
            return

        stats = self.trade_manager.get_estatisticas()
        saldo = self.deriv_bridge.get_balance() if self.deriv_bridge else self.saldo_inicial

        ml_tag = "🧠" if self.ml_enabled else "🎲"

        print(f"\r{ml_tag} Saldo: ${saldo:.2f} | Lucro: ${stats['lucro_liquido']:+.2f} | " +
              f"Trades: {stats['total_trades']} | Win: {stats['win_rate']:.1f}% | " +
              f"Próximo: ${stats['stake_atual']:.2f}", end="", flush=True)

    def iniciar_robo(self):
        """Wrapper síncrono"""
        # Cria event loop em thread separada
        self.loop = asyncio.new_event_loop()

        def run_loop():
            asyncio.set_event_loop(self.loop)
            self.loop.run_until_complete(self.iniciar_robo_async())

        self.loop_thread = Thread(target=run_loop, daemon=True)
        self.loop_thread.start()
        self.loop_thread.join()

    def ver_historico(self):
        """Ver histórico"""
        if not self.trade_manager:
            print("📊 Robô não iniciado ainda")
            return

        hist = self.trade_manager.get_historico_recente(20)

        if not hist:
            print("📊 Nenhum trade executado")
            return

        print("\n" + "=" * 70)
        print("📊 HISTÓRICO (Últimos 20)")
        print("=" * 70)
        print(f"{'Data/Hora':<20} {'Tipo':<15} {'Stake':<10} {'Resultado':<12} {'Profit':<10}")
        print("-" * 70)

        for trade in hist[-20:]:
            timestamp = trade['timestamp'].strftime('%d/%m %H:%M:%S')
            tipo = trade['params']['contract_type']
            stake = f"${trade['stake']:.2f}"
            resultado = "✅ WIN" if trade['vitoria'] else "❌ LOSS"
            profit = f"${trade['profit']:+.2f}"

            print(f"{timestamp:<20} {tipo:<15} {stake:<10} {resultado:<12} {profit:<10}")

        print("=" * 70)

    def menu_principal(self):
        """Menu"""
        self.print_header()

        while True:
            self.mostrar_configuracao()

            print("╔" + "═" * 68 + "╗")
            print("║" + " MENU PRINCIPAL".center(68) + "║")
            print("╠" + "═" * 68 + "╣")
            print("║  1. 🎮 Modo de Operação (Simulado/Demo/Real)" + " " * 24 + "║")
            print("║  2. ⚡ Modo de Velocidade" + " " * 42 + "║")
            print("║  3. 📊 Selecionar Mercado" + " " * 42 + "║")
            print("║  4. 🎯 Selecionar Tipo" + " " * 45 + "║")
            print("║  5. ⚙️ Configurar Parâmetros" + " " * 40 + "║")
            print("║  6. 🚀 INICIAR ROBÔ" + " " * 49 + "║")
            print("║  7. 📊 Ver Histórico" + " " * 47 + "║")
            print("║  0. ❌ Sair" + " " * 56 + "║")
            print("╚" + "═" * 68 + "╝\n")

            try:
                choice = input("👉 Escolha uma opção: ")

                if choice == "0":
                    print("\n👋 Até logo!")
                    break
                elif choice == "1":
                    self.selecionar_modo_operacao()
                elif choice == "2":
                    self.configurar_modo_velocidade()
                elif choice == "3":
                    self.configurar_mercado()
                elif choice == "4":
                    self.configurar_tipo_contrato()
                elif choice == "5":
                    self.configurar_parametros()
                elif choice == "6":
                    self.iniciar_robo()
                elif choice == "7":
                    self.ver_historico()
                else:
                    print("❌ Opção inválida!")

            except KeyboardInterrupt:
                print("\n\n👋 Até logo!")
                break
            except Exception as e:
                print(f"❌ Erro: {e}")


if __name__ == "__main__":
    bot = IAAvancadoReal()
    bot.menu_principal()