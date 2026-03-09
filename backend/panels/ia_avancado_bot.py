"""
ALPHA DOLAR 2.0 - IA AVANÇADO
Painel de configuração e execução da IA Avançada
MELHOR QUE O DC BOTS!
"""

import sys
import os
import time
from datetime import datetime

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


class IAAvancado:
    """Bot IA Avançado - Automático e Inteligente"""

    def __init__(self):
        self.name = "ALPHA DOLAR 2.0 - IA AVANÇADO"
        self.version = "1.0.0"

        # Configurações padrão
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
            'modo_operacao': 'balanceado',  # baixo_risco, preciso, balanceado, veloz
            'confianca_minima': 0.55
        }

        # Modos de operação
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
        self.is_running = False

        # Saldo simulado
        self.saldo_demo = 100.0

    def print_header(self):
        """Cabeçalho bonito"""
        print("\n" + "=" * 70)
        print(f"🤖 {self.name} v{self.version}")
        print("=" * 70)
        print("💡 Sistema de IA com gerenciamento automático de trades")
        print("📊 Martingale inteligente + Análise de padrões")
        print("=" * 70 + "\n")

    def print_box(self, title, content, color="blue"):
        """Caixa bonita para exibir informações"""
        emojis = {
            "blue": "💙",
            "green": "💚",
            "red": "❤️",
            "yellow": "💛"
        }

        print(f"\n{emojis.get(color, '💙')} ╔{'═' * 66}╗")
        print(f"  ║ {title:^64} ║")
        print(f"  ╠{'═' * 66}╣")
        for line in content:
            print(f"  ║ {line:64} ║")
        print(f"  ╚{'═' * 66}╝\n")

    def configurar_modo_operacao(self):
        """Configura o modo de operação"""
        print("\n" + "=" * 70)
        print("🎮 MODO DE OPERAÇÃO")
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

                # Verifica se é premium
                if modo['premium']:
                    print("\n⚠️ Este modo é PREMIUM!")
                    confirma = input("Você tem acesso premium? (s/n): ")
                    if confirma.lower() != 's':
                        print("❌ Modo não disponível. Escolha outro modo.")
                        return self.configurar_modo_operacao()

                self.config['modo_operacao'] = modo_key
                self.config['confianca_minima'] = modo['confianca']
                print(f"\n✅ Modo selecionado: {modo['name']}")

        except (ValueError, IndexError):
            print("❌ Opção inválida!")

    def configurar_mercado(self):
        """Seleciona mercado"""
        print("\n" + "=" * 70)
        print("📊 SELECIONAR MERCADO")
        print("=" * 70)

        # Exibe categorias principais
        principais = [
            ("volatility_continuous", "📊 Índices de Volatilidade"),
            ("crash_boom", "💥 Crash/Boom"),
            ("volatility_jump", "🦘 Jump Indices")
        ]

        for idx, (key, name) in enumerate(principais, 1):
            markets = get_markets_by_category(key)
            print(f"{idx}. {name} ({len(markets)} mercados)")

        print(f"{len(principais) + 1}. 🌐 Ver todos os mercados")
        print("0. ⬅️ Manter atual")

        try:
            choice = int(input(f"\n👉 Escolha (atual: {self.config['market_name']}): ") or "0")

            if choice == 0:
                return

            if 1 <= choice <= len(principais):
                key, _ = principais[choice - 1]
                markets = get_markets_by_category(key)

                # Lista mercados
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

        # Tipos mais usados
        populares = [
            ("DIGITODD", "🔴 Ímpar"),
            ("DIGITEVEN", "🔵 Par"),
            ("CALL", "⬆️ Rise"),
            ("PUT", "⬇️ Fall"),
            ("DIGITOVER", "⬆️ Over (Superior)"),
            ("DIGITUNDER", "⬇️ Under (Inferior)")
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

                # Se for OVER/UNDER, pede barreira
                if tipo in ['DIGITOVER', 'DIGITUNDER']:
                    barrier = int(input("👉 Digite a barreira (0-9): "))
                    if 0 <= barrier <= 9:
                        self.config['barrier'] = barrier
                        print(f"✅ Barreira: {barrier}")
                else:
                    self.config['barrier'] = None

                print(f"✅ Tipo: {nome}")

        except (ValueError, IndexError):
            print("❌ Opção inválida!")

    def configurar_parametros(self):
        """Configura parâmetros de trading"""
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

        print(f"\n🎮 Perdas Virtuais (atual: {self.config['perdas_virtuais']})")
        p_virtual = input("👉 Quantas perdas antes de entrar real: ") or str(self.config['perdas_virtuais'])
        self.config['perdas_virtuais'] = int(p_virtual)

        if self.config['perdas_virtuais'] > 0:
            self.config['modo_virtual'] = 'na_perda'
            self.config['iniciar_com_virtuais'] = True
        else:
            self.config['modo_virtual'] = 'nunca'
            self.config['iniciar_com_virtuais'] = False

        print("\n✅ Parâmetros configurados!")

    def mostrar_configuracao(self):
        """Mostra configuração atual"""
        stats = self.trade_manager.get_estatisticas() if self.trade_manager else None

        lucro_display = f"${stats['lucro_liquido']:+.2f} ({stats['roi']:+.1f}%)" if stats else "$0.00 (0%)"

        modo_atual = self.modos.get(self.config['modo_operacao'], self.modos['balanceado'])
        modo_display = modo_atual['name']

        content = [
            f"💰 Lucro: {lucro_display}",
            "",
            f"🎮 Modo: {modo_display}",
            f"📊 Mercado: {self.config['market_name']}",
            f"🎯 Tipo: {self.config['contract_name']}",
            "",
            f"💵 Stake Inicial: ${self.config['stake_inicial']:.2f}",
            f"📈 Multiplicador: {self.config['multiplicador']:.1f}x",
            f"🎯 Lucro Alvo: ${self.config['lucro_alvo']:.2f}",
            f"🛑 Stop Loss: ${self.config['limite_perda']:.2f}",
            f"🎮 Perdas Virtuais: {self.config['perdas_virtuais']}",
            ""
        ]

        if stats:
            content.extend([
                f"📊 Trades: {stats['total_trades']} (V:{stats['vitorias']} D:{stats['derrotas']})",
                f"📈 Win Rate: {stats['win_rate']:.1f}%",
                f"💰 Próximo Stake: ${stats['stake_atual']:.2f}",
                f"🎮 Modo Virtual: {'SIM' if stats['modo_virtual_ativo'] else 'NÃO'}"
            ])

        self.print_box("CONFIGURAÇÕES DA IA AVANÇADA", content, "blue")

    def iniciar_robo(self):
        """Inicia o robô"""
        # Seleciona estratégia automaticamente baseada no tipo de contrato
        contract_type = self.config['contract_type']

        if contract_type in ['DIGITODD', 'DIGITEVEN', 'DIGITOVER', 'DIGITUNDER', 'DIGITMATCH', 'DIGITDIFF']:
            strategy = "digit_pattern"
            print("🧠 Estratégia: Análise de Padrões de Dígitos")
        elif contract_type in ['CALL', 'PUT', 'CALLE', 'PUTE']:
            strategy = "trend_following"
            print("🧠 Estratégia: Seguimento de Tendência")
        else:
            strategy = "smart_random"
            print("🧠 Estratégia: Análise Probabilística")

        # Inicializa componentes
        self.ai_engine = AIEngine(strategy_type=strategy)
        self.trade_manager = TradeManager(self.config)
        self.trade_manager.set_saldo_inicial(self.saldo_demo)

        self.is_running = True

        print("\n" + "=" * 70)
        print("🚀 ROBÔ INICIADO!")
        print("=" * 70)
        print("💡 Pressione Ctrl+C para pausar")
        print("=" * 70 + "\n")

        try:
            tick_count = 0
            ticks_simulados = []

            # Pega intervalo do modo
            modo_config = self.modos.get(self.config['modo_operacao'], self.modos['balanceado'])
            intervalo_analise = modo_config['intervalo']

            print(f"🎮 Modo: {modo_config['name']}")
            print(f"📊 Analisando a cada {intervalo_analise} ticks")
            print(f"🎯 Confiança mínima: {modo_config['confianca']:.0%}\n")

            while self.is_running:
                # Simula recebimento de ticks
                tick_count += 1
                novo_tick = 10000 + (tick_count % 100) * 0.5
                ticks_simulados.append(novo_tick)

                # Mantém últimos 100 ticks
                if len(ticks_simulados) > 100:
                    ticks_simulados = ticks_simulados[-100:]

                # Analisa baseado no intervalo do modo
                if tick_count % intervalo_analise == 0 and len(ticks_simulados) >= 10:
                    self.processar_analise(ticks_simulados)

                # Exibe status a cada 10 ticks
                if tick_count % 10 == 0:
                    self.mostrar_status()

                # Aguarda próximo tick (simulado)
                time.sleep(1)

        except KeyboardInterrupt:
            print("\n\n⏸️ Robô pausado!")
            self.is_running = False

    def analise_veloz(self, ticks):
        """Análise ULTRA RÁPIDA para modo Veloz"""
        import random

        if len(ticks) < 5:
            return {'should_trade': False, 'reason': 'Aguardando ticks'}

        contract_type = self.config['contract_type']

        # Extrai últimos 5 dígitos
        digits = [int(str(float(t)).replace('.', '')[-1]) for t in ticks[-5:]]
        even = sum(1 for d in digits if d % 2 == 0)
        odd = len(digits) - even

        # PAR
        if contract_type == 'DIGITEVEN':
            if odd >= 3 or random.random() < 0.6:
                return {
                    'should_trade': True,
                    'contract_type': 'DIGITEVEN',
                    'confidence': 0.50 + random.uniform(0, 0.15),
                    'reason': f'Veloz: {odd} ímpares detectados'
                }

        # ÍMPAR
        elif contract_type == 'DIGITODD':
            if even >= 3 or random.random() < 0.6:
                return {
                    'should_trade': True,
                    'contract_type': 'DIGITODD',
                    'confidence': 0.50 + random.uniform(0, 0.15),
                    'reason': f'Veloz: {even} pares detectados'
                }

        # CALL/PUT
        elif contract_type in ['CALL', 'PUT']:
            last_change = ticks[-1] - ticks[-2]

            if contract_type == 'CALL' and (last_change > 0 or random.random() < 0.6):
                return {
                    'should_trade': True,
                    'contract_type': 'CALL',
                    'confidence': 0.55,
                    'reason': 'Veloz: Movimento de alta'
                }
            elif contract_type == 'PUT' and (last_change < 0 or random.random() < 0.6):
                return {
                    'should_trade': True,
                    'contract_type': 'PUT',
                    'confidence': 0.55,
                    'reason': 'Veloz: Movimento de baixa'
                }

        return {'should_trade': False, 'reason': 'Aguardando'}

    def processar_analise(self, ticks):
        """Processa análise e executa trade se necessário"""
        # Modo VELOZ = análise simplificada e rápida
        if self.config['modo_operacao'] == 'veloz':
            decision = self.analise_veloz(ticks)
        else:
            # IA analisa normalmente
            decision = self.ai_engine.analyze(ticks, self.config)

        # Filtra por confiança mínima do modo
        confianca_minima = self.config['confianca_minima']
        confidence = decision.get('confidence', 0)

        # Se confiança for muito baixa, não opera
        if decision.get('should_trade') and confidence < confianca_minima:
            decision['should_trade'] = False
            decision['reason'] = f"Confiança {confidence:.0%} < mínima {confianca_minima:.0%}"

        # Prepara trade
        params = self.trade_manager.preparar_trade(decision)

        if params:
            # Simula execução
            print(f"\n🎯 EXECUTANDO TRADE:")
            print(f"   Tipo: {params['contract_type']}")
            print(f"   Stake: ${params['amount']:.2f}")
            print(f"   Virtual: {'SIM' if params['is_virtual'] else 'NÃO'}")

            # Simula resultado (65% win rate - mais realista)
            import random
            vitoria = random.random() < 0.65

            profit = params['amount'] * 0.95 if vitoria else -params['amount']

            resultado = {
                'status': 'won' if vitoria else 'lost',
                'profit': profit,
                'contract_id': f"DEMO_{int(time.time())}"
            }

            # Registra
            self.trade_manager.registrar_trade(params, resultado)

            emoji = "🎉" if vitoria else "😞"
            print(f"   {emoji} {'VITÓRIA' if vitoria else 'DERROTA'}: ${profit:+.2f}")

    def mostrar_status(self):
        """Mostra status em tempo real"""
        if not self.trade_manager:
            return

        stats = self.trade_manager.get_estatisticas()

        print(f"\r💰 Saldo: ${stats['saldo_atual']:.2f} | " +
              f"Lucro: ${stats['lucro_liquido']:+.2f} | " +
              f"Trades: {stats['total_trades']} | " +
              f"Win Rate: {stats['win_rate']:.1f}% | " +
              f"Próximo: ${stats['stake_atual']:.2f}", end="", flush=True)

    def ver_historico(self):
        """Exibe histórico de trades"""
        if not self.trade_manager:
            print("❌ Robô não foi iniciado ainda!")
            return

        historico = self.trade_manager.get_historico_recente(20)

        if not historico:
            print("📊 Nenhum trade executado ainda")
            return

        print("\n" + "=" * 70)
        print("📊 HISTÓRICO DE TRADES (Últimos 20)")
        print("=" * 70)
        print(f"{'Data/Hora':<20} {'Tipo':<15} {'Stake':<10} {'Resultado':<12} {'Profit':<10}")
        print("-" * 70)

        for trade in historico[-20:]:
            timestamp = trade['timestamp'].strftime('%d/%m %H:%M:%S')
            tipo = trade['params']['contract_type']
            stake = f"${trade['stake']:.2f}"
            resultado = "✅ VITÓRIA" if trade['vitoria'] else "❌ DERROTA"
            profit = f"${trade['profit']:+.2f}"
            virtual = " 🎮" if trade['is_virtual'] else ""

            print(f"{timestamp:<20} {tipo:<15} {stake:<10} {resultado:<12} {profit:<10}{virtual}")

        print("=" * 70)

    def menu_principal(self):
        """Menu principal"""
        self.print_header()

        while True:
            self.mostrar_configuracao()

            print("╔" + "═" * 68 + "╗")
            print("║" + " MENU PRINCIPAL".center(68) + "║")
            print("╠" + "═" * 68 + "╣")
            print("║  1. 🎮 Modo de Operação" + " " * 44 + "║")
            print("║  2. 📊 Selecionar Mercado" + " " * 42 + "║")
            print("║  3. 🎯 Selecionar Tipo de Negociação" + " " * 32 + "║")
            print("║  4. ⚙️ Configurar Parâmetros" + " " * 40 + "║")
            print("║  5. 🚀 INICIAR ROBÔ" + " " * 49 + "║")
            print("║  6. 📊 Ver Histórico" + " " * 47 + "║")
            print("║  0. ❌ Sair" + " " * 56 + "║")
            print("╚" + "═" * 68 + "╝\n")

            try:
                choice = input("👉 Escolha uma opção: ")

                if choice == "0":
                    print("\n👋 Até logo!")
                    break
                elif choice == "1":
                    self.configurar_modo_operacao()
                elif choice == "2":
                    self.configurar_mercado()
                elif choice == "3":
                    self.configurar_tipo_contrato()
                elif choice == "4":
                    self.configurar_parametros()
                elif choice == "5":
                    self.iniciar_robo()
                elif choice == "6":
                    self.ver_historico()
                else:
                    print("❌ Opção inválida!")

            except KeyboardInterrupt:
                print("\n\n👋 Até logo!")
                break
            except Exception as e:
                print(f"❌ Erro: {e}")


if __name__ == "__main__":
    bot = IAAvancado()
    bot.menu_principal()