"""
ALPHA DOLAR 2.0 - Painel IA Avançada
Estratégias VIP e Premium (Rise/Fall + Dígitos)
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from config import BotConfig, validate_config
from bot import AlphaDolar

# ===== ESTRATÉGIAS DISPONÍVEIS =====
ESTRATEGIAS_VIP = {
    "digit_sniper": {
        "nome": "Digit Sniper",
        "descricao": "Sniper: entra contra o dígito mais quente",
        "tipo": "DIGITOVER/DIGITUNDER",
        "tier": "VIP"
    },
    "digit_pulse": {
        "nome": "Digit Pulse",
        "descricao": "Detecta pulsos e entra na reversão",
        "tipo": "DIGITOVER/DIGITUNDER",
        "tier": "VIP"
    },
}

ESTRATEGIAS_PREMIUM = {
    "mega_digit_1": {
        "nome": "Mega Digit 1.0",
        "descricao": "Score combinado: frequência + pulso + par/ímpar",
        "tipo": "DIGITOVER/DIGITUNDER",
        "tier": "PREMIUM"
    },
    "mega_digit_2": {
        "nome": "Mega Digit 2.0",
        "descricao": "Janelas 25/50/100 ticks com pesos diferentes",
        "tipo": "DIGITOVER/DIGITUNDER",
        "tier": "PREMIUM"
    },
}

# ===== MERCADOS SUPORTADOS PARA DÍGITOS =====
MERCADOS_DIGIT = {
    "R_10":    "Volatility 10 Index   ← Recomendado para dígitos",
    "R_25":    "Volatility 25 Index",
    "R_50":    "Volatility 50 Index",
    "R_75":    "Volatility 75 Index",
    "R_100":   "Volatility 100 Index",
    "1HZ10V":  "Volatility 10 (1s) Index",
    "1HZ25V":  "Volatility 25 (1s) Index",
    "1HZ50V":  "Volatility 50 (1s) Index",
    "1HZ100V": "Volatility 100 (1s) Index",
}

# ===== HELPERS =====

def limpar_tela():
    os.system('clear' if os.name == 'posix' else 'cls')

def print_header():
    print("\n" + "="*70)
    print("🧠 ALPHA DOLAR 2.0 - IA AVANÇADA")
    print("="*70)

def selecionar_mercado():
    print("\n" + "="*70)
    print("📊 SELECIONE O MERCADO (Dígitos)")
    print("="*70 + "\n")
    mercados = list(MERCADOS_DIGIT.items())
    for idx, (simbolo, nome) in enumerate(mercados, 1):
        print(f"{idx:2d} - {nome} ({simbolo})")
    print("\n 0 - Voltar")
    print("="*70)
    while True:
        try:
            escolha = input("\n👉 Escolha: ").strip()
            if escolha == "0":
                return None
            idx = int(escolha) - 1
            if 0 <= idx < len(mercados):
                simbolo, nome = mercados[idx]
                print(f"\n✅ Selecionado: {nome} ({simbolo})")
                return simbolo
            print("❌ Opção inválida!")
        except ValueError:
            print("❌ Digite um número válido!")

def selecionar_estrategia():
    print("\n" + "="*70)
    print("🎯 SELECIONE A ESTRATÉGIA")
    print("="*70)

    todas = []

    print("\n🟢 VIP")
    print("-"*50)
    for key, info in ESTRATEGIAS_VIP.items():
        todas.append((key, info))
        idx = len(todas)
        print(f"{idx:2d} - {info['nome']}")
        print(f"     {info['descricao']}")
        print(f"     Tipo: {info['tipo']}\n")

    print("🟡 PREMIUM")
    print("-"*50)
    for key, info in ESTRATEGIAS_PREMIUM.items():
        todas.append((key, info))
        idx = len(todas)
        print(f"{idx:2d} - {info['nome']}")
        print(f"     {info['descricao']}")
        print(f"     Tipo: {info['tipo']}\n")

    print(" 0 - Voltar")
    print("="*70)

    while True:
        try:
            escolha = input(f"\n👉 Escolha (1-{len(todas)}): ").strip()
            if escolha == "0":
                return None, None
            idx = int(escolha) - 1
            if 0 <= idx < len(todas):
                key, info = todas[idx]
                print(f"\n✅ Selecionado: {info['nome']} [{info['tier']}]")
                return key, info
            print("❌ Opção inválida!")
        except ValueError:
            print("❌ Digite um número válido!")

def configurar_valores():
    print("\n" + "="*70)
    print("💰 CONFIGURAÇÃO DE VALORES")
    print("="*70 + "\n")
    while True:
        try:
            stake = float(input("💵 Stake inicial [$0.35 - $100]: $").strip())
            if 0.35 <= stake <= 100:
                break
            print("❌ Valor fora do intervalo!")
        except ValueError:
            print("❌ Digite um número válido!")
    while True:
        try:
            lucro = float(input("🎯 Lucro alvo [$1 - $1000]: $").strip())
            if 1 <= lucro <= 1000:
                break
            print("❌ Valor fora do intervalo!")
        except ValueError:
            print("❌ Digite um número válido!")
    while True:
        try:
            perda = float(input("🛑 Limite de perda [$1 - $1000]: $").strip())
            if 1 <= perda <= 1000:
                break
            print("❌ Valor fora do intervalo!")
        except ValueError:
            print("❌ Digite um número válido!")
    return {"stake": stake, "lucro_alvo": lucro, "limite_perda": perda}

def configurar_martingale():
    resp = input("\n⚠️  Deseja usar Martingale? (s/n): ").strip().lower()
    usar = resp == 's'
    print("✅ Martingale ATIVADO" if usar else "❌ Martingale DESATIVADO")
    return usar

def exibir_resumo(config):
    print("\n" + "="*70)
    print("📋 RESUMO DA CONFIGURAÇÃO")
    print("="*70)
    print(f"\n📊 Mercado:    {config['mercado']}")
    print(f"🎯 Estratégia: {config['estrategia_nome']} [{config['tier']}]")
    print(f"💡 Tipo:       {config['tipo']}")
    print(f"\n💰 Stake:      ${config['valores']['stake']:.2f}")
    print(f"🎯 Lucro alvo: ${config['valores']['lucro_alvo']:.2f}")
    print(f"🛑 Stop loss:  ${config['valores']['limite_perda']:.2f}")
    print(f"⚡ Martingale: {'Ativado' if config['martingale'] else 'Desativado'}")
    print("\n" + "="*70)
    return input("\n✅ Confirma? (s/n): ").strip().lower() == 's'

def iniciar_ia_avancada():
    limpar_tela()
    print_header()

    mercado = selecionar_mercado()
    if mercado is None:
        return

    estrategia_key, estrategia_info = selecionar_estrategia()
    if estrategia_key is None:
        return

    valores = configurar_valores()
    martingale = configurar_martingale()

    config = {
        "mercado": mercado,
        "estrategia_key": estrategia_key,
        "estrategia_nome": estrategia_info["nome"],
        "tier": estrategia_info["tier"],
        "tipo": estrategia_info["tipo"],
        "valores": valores,
        "martingale": martingale,
    }

    if not exibir_resumo(config):
        print("\n❌ Cancelado!")
        input("\nPressione ENTER para voltar...")
        return

    # Aplica configurações
    BotConfig.DEFAULT_SYMBOL = config['mercado']
    BotConfig.STAKE_INICIAL   = config['valores']['stake']
    BotConfig.LUCRO_ALVO      = config['valores']['lucro_alvo']
    BotConfig.LIMITE_PERDA    = config['valores']['limite_perda']

    if not validate_config():
        input("\nPressione ENTER para voltar...")
        return

    print(f"\n🚀 Carregando {config['estrategia_nome']}...")

    try:
        from strategies import get_strategy
        estrategia = get_strategy(config['estrategia_key'])
    except Exception as e:
        print(f"❌ Erro ao carregar estratégia: {e}")
        input("\nPressione ENTER para voltar...")
        return

    bot = AlphaDolar(
        strategy=estrategia,
        use_martingale=config['martingale']
    )
    bot.start()


if __name__ == "__main__":
    iniciar_ia_avancada()