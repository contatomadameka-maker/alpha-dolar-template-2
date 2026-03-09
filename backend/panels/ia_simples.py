"""
ALPHA DOLAR 2.0 - Painel IA Simples
Menu completo para operação com IA Simples (Alpha Bots 1-17)
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from config import BotConfig, validate_config
from bot import AlphaDolar

# ===== DADOS DOS MERCADOS =====
MERCADOS = {
    "VOLATILITY_CONTINUOUS": {
        "titulo": "📊 Índices Continuous",
        "opcoes": {
            "R_100": "Volatility 100 Index",
            "1HZ100V": "Volatility 100 (1s) Index",
            "1HZ90V": "Volatility 90 (1s) Index",
            "R_75": "Volatility 75 Index",
            "1HZ75V": "Volatility 75 (1s) Index",
            "R_50": "Volatility 50 Index",
            "1HZ50V": "Volatility 50 (1s) Index",
            "1HZ30V": "Volatility 30 (1s) Index",
            "R_25": "Volatility 25 Index",
            "1HZ25V": "Volatility 25 (1s) Index",
            "1HZ15V": "Volatility 15 (1s) Index",
            "R_10": "Volatility 10 Index",
            "1HZ10V": "Volatility 10 (1s) Index",
        }
    },
    "DAILY_RESET": {
        "titulo": "📈 Índices Daily Reset",
        "opcoes": {
            "RDBULL": "Bull Market Index",
            "RDBEAR": "Bear Market Index",
        }
    },
    "JUMP": {
        "titulo": "🦘 Índices Jump",
        "opcoes": {
            "JD100": "Jump 100 Index",
            "JD75": "Jump 75 Index",
            "JD50": "Jump 50 Index",
            "JD25": "Jump 25 Index",
            "JD10": "Jump 10 Index",
        }
    }
}

# ===== ESTRATÉGIAS =====
ESTRATEGIAS = {
    "ALPHA_BOTS": {
        "titulo": "🤖 Alpha Bots (Gratuitos)",
        "opcoes": {
            "alpha_bot_1": "Alpha Bot 1  — Rise/Fall (Tendência SMA)",
            "alpha_bot_2": "Alpha Bot 2  — Rise/Fall (Reversão Suporte/Resistência)",
            "alpha_bot_3": "Alpha Bot 3  — Rise/Fall (Momentum EMA)",
            "alpha_bot_4": "Alpha Bot 4  — Dígitos (Frequência Over/Under)",
        }
    }
}

# ===== MODOS DE NEGOCIAÇÃO =====
MODOS_NEGOCIACAO = {
    "baixo_risco": {
        "nome": "🛡️ Baixo Risco",
        "descricao": "Máxima precisão, menos negociações",
        "icone": "🛡️"
    },
    "preciso": {
        "nome": "🎯 Preciso",
        "descricao": "Menos negociações, mais precisão",
        "icone": "🎯"
    },
    "balanceado": {
        "nome": "⚖️ Balanceado",
        "descricao": "Negociações e precisão balanceada",
        "icone": "⚖️"
    },
    "veloz": {
        "nome": "⚡ Veloz",
        "descricao": "Mais negociações, menos precisão",
        "icone": "⚡"
    }
}

# ===== GERENCIAMENTO DE RISCO =====
GERENCIAMENTO_RISCO = {
    "quantia_fixa": {
        "nome": "💵 Quantia Fixa",
        "descricao": "Baixo risco (min $10)",
        "saldo_minimo": 10.0
    },
    "conservador": {
        "nome": "🛡️ Conservador",
        "descricao": "Baixo risco (min $50)",
        "saldo_minimo": 50.0
    },
    "otimizado": {
        "nome": "📊 Otimizado",
        "descricao": "Médio risco (min $100)",
        "saldo_minimo": 100.0
    },
    "agressivo": {
        "nome": "🚀 Agressivo",
        "descricao": "Alto risco (min $200)",
        "saldo_minimo": 200.0
    }
}

# ===== FUNÇÕES DE MENU =====

def limpar_tela():
    os.system('clear' if os.name == 'posix' else 'cls')

def print_header():
    print("\n" + "="*70)
    print("🤖 ALPHA DOLAR 2.0 - IA SIMPLES")
    print("="*70)

def selecionar_mercado():
    print("\n" + "="*70)
    print("📊 SELECIONE O MERCADO")
    print("="*70 + "\n")

    for categoria in MERCADOS.values():
        print(f"\n{categoria['titulo']}")
        print("-" * 50)
        for simbolo, nome in categoria['opcoes'].items():
            print(f"  • {nome} ({simbolo})")

    print("\n" + "="*70)
    print("\n💡 Digite o símbolo do mercado (ex: R_100, JD50, etc.)")

    while True:
        escolha = input("\n👉 Mercado: ").strip().upper()
        for categoria in MERCADOS.values():
            if escolha in categoria['opcoes']:
                print(f"\n✅ Selecionado: {categoria['opcoes'][escolha]} ({escolha})")
                return escolha
        print("❌ Mercado inválido! Tente novamente.")

def selecionar_estrategia():
    print("\n" + "="*70)
    print("🎯 SELECIONE A ESTRATÉGIA")
    print("="*70 + "\n")

    print(ESTRATEGIAS['ALPHA_BOTS']['titulo'])
    print("-" * 50)

    opcoes = list(ESTRATEGIAS['ALPHA_BOTS']['opcoes'].items())
    for idx, (key, nome) in enumerate(opcoes, 1):
        print(f"{idx:2d} - {nome}")

    print("\n 0 - Voltar")
    print("="*70)

    while True:
        try:
            escolha = input(f"\n👉 Escolha (1-{len(opcoes)}): ").strip()
            if escolha == "0":
                return None
            idx = int(escolha) - 1
            if 0 <= idx < len(opcoes):
                key, nome = opcoes[idx]
                print(f"\n✅ Selecionado: {nome}")
                return key
            print("❌ Opção inválida!")
        except ValueError:
            print("❌ Digite um número válido!")

def selecionar_modo_negociacao():
    print("\n" + "="*70)
    print("⚡ SELECIONE O MODO DE NEGOCIAÇÃO")
    print("="*70 + "\n")

    modos = list(MODOS_NEGOCIACAO.items())
    for idx, (key, info) in enumerate(modos, 1):
        print(f"{idx} - {info['icone']} {info['nome']}")
        print(f"    {info['descricao']}\n")

    print("="*70)

    while True:
        try:
            escolha = input("\n👉 Escolha (1-4): ").strip()
            idx = int(escolha) - 1
            if 0 <= idx < len(modos):
                key, info = modos[idx]
                print(f"\n✅ Modo selecionado: {info['nome']}")
                return key
            print("❌ Opção inválida!")
        except ValueError:
            print("❌ Digite um número válido!")

def configurar_valores():
    print("\n" + "="*70)
    print("💰 CONFIGURAÇÃO DE VALORES")
    print("="*70 + "\n")

    while True:
        try:
            stake = float(input("💵 Quantia inicial (stake) [$0.35 - $100]: $").strip())
            if 0.35 <= stake <= 100:
                break
            print("❌ Valor fora do intervalo permitido!")
        except ValueError:
            print("❌ Digite um valor numérico válido!")

    while True:
        try:
            lucro = float(input("🎯 Lucro alvo (stop gain) [$1 - $1000]: $").strip())
            if 1 <= lucro <= 1000:
                break
            print("❌ Valor fora do intervalo permitido!")
        except ValueError:
            print("❌ Digite um valor numérico válido!")

    while True:
        try:
            perda = float(input("🛑 Limite de perda (stop loss) [$1 - $1000]: $").strip())
            if 1 <= perda <= 1000:
                break
            print("❌ Valor fora do intervalo permitido!")
        except ValueError:
            print("❌ Digite um valor numérico válido!")

    return {"stake": stake, "lucro_alvo": lucro, "limite_perda": perda}

def selecionar_gerenciamento_risco():
    print("\n" + "="*70)
    print("🛡️ GERENCIAMENTO DE RISCO")
    print("="*70 + "\n")

    riscos = list(GERENCIAMENTO_RISCO.items())
    for idx, (key, info) in enumerate(riscos, 1):
        print(f"{idx} - {info['nome']}")
        print(f"    {info['descricao']}\n")

    print("="*70)

    while True:
        try:
            escolha = input("\n👉 Escolha (1-4): ").strip()
            idx = int(escolha) - 1
            if 0 <= idx < len(riscos):
                key, info = riscos[idx]
                print(f"\n✅ Gerenciamento selecionado: {info['nome']}")
                return key
            print("❌ Opção inválida!")
        except ValueError:
            print("❌ Digite um número válido!")

def configurar_martingale():
    print("\n⚠️ Deseja usar Martingale? (s/n): ", end="")
    usar = input().strip().lower() == 's'
    print("✅ Martingale ATIVADO" if usar else "❌ Martingale DESATIVADO")
    return usar

def exibir_resumo_configuracao(config):
    print("\n" + "="*70)
    print("📋 RESUMO DA CONFIGURAÇÃO")
    print("="*70)
    print(f"\n📊 Mercado:    {config['mercado']}")
    print(f"🎯 Estratégia: {config['estrategia']}")
    print(f"⚡ Modo:       {config['modo']}")
    print(f"🛡️ Risco:      {config['risco']}")
    print(f"\n💰 Stake Inicial: ${config['valores']['stake']:.2f}")
    print(f"🎯 Lucro Alvo:    ${config['valores']['lucro_alvo']:.2f}")
    print(f"🛑 Limite Perda:  ${config['valores']['limite_perda']:.2f}")
    print(f"\n⚡ Martingale: {'Ativado' if config['martingale'] else 'Desativado'}")
    print("\n" + "="*70)
    return input("\n✅ Confirma essa configuração? (s/n): ").strip().lower() == 's'

def iniciar_ia_simples():
    limpar_tela()
    print_header()

    mercado = selecionar_mercado()
    estrategia = selecionar_estrategia()

    if estrategia is None:
        print("\n🔙 Voltando ao menu principal...")
        return

    modo = selecionar_modo_negociacao()
    valores = configurar_valores()
    risco = selecionar_gerenciamento_risco()
    martingale = configurar_martingale()

    config = {
        "mercado": mercado,
        "estrategia": estrategia,
        "modo": modo,
        "valores": valores,
        "risco": risco,
        "martingale": martingale
    }

    if not exibir_resumo_configuracao(config):
        print("\n❌ Configuração cancelada!")
        input("\nPressione ENTER para voltar ao menu...")
        return

    BotConfig.DEFAULT_SYMBOL   = config['mercado']
    BotConfig.STAKE_INICIAL    = config['valores']['stake']
    BotConfig.LUCRO_ALVO       = config['valores']['lucro_alvo']
    BotConfig.LIMITE_PERDA     = config['valores']['limite_perda']
    BotConfig.TRADING_MODE     = config['modo']
    BotConfig.RISK_MANAGEMENT  = config['risco']

    if not validate_config():
        input("\nPressione ENTER para voltar ao menu...")
        return

    print("\n🚀 Iniciando bot com IA Simples...")
    print("⏳ Carregando estratégia...")

    try:
        from strategies import get_strategy
        strategy = get_strategy(config['estrategia'])
    except Exception as e:
        print(f"❌ Erro ao carregar estratégia: {e}")
        input("\nPressione ENTER para voltar ao menu...")
        return

    bot = AlphaDolar(
        strategy=strategy,
        use_martingale=config['martingale']
    )
    bot.start()

if __name__ == "__main__":
    iniciar_ia_simples()