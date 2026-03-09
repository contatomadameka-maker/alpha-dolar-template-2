"""
ALPHA DOLAR 2.0 - Bot de Trading Automatizado
Menu Principal - Seleção de Modo de Operação
"""
import sys
import os

# Adiciona o diretório panels ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'panels'))

def print_header():
    """Exibe o cabeçalho principal"""
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║              💰 ALPHA DOLAR 2.0                              ║
    ║                                                              ║
    ║          Bot de Trading Automatizado para Deriv              ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """)

def print_menu():
    """Exibe o menu principal"""
    print("\n" + "="*70)
    print("🎮 SELECIONE O MODO DE OPERAÇÃO")
    print("="*70)
    print("\n📋 MODOS DISPONÍVEIS:\n")
    print("1 - 🎯 Manual           → Controle total das operações")
    print("2 - 🤖 IA Simples       → Trading automatizado (Alpha Bots 1-17)")
    print("3 - 🧠 IA Avançada      → Estratégias VIP e Premium")
    print("0 - ❌ Sair\n")
    print("="*70)

def main():
    """Função principal"""
    while True:
        print_header()
        print_menu()

        escolha = input("\n👉 Escolha o modo (0-3): ").strip()

        if escolha == "0":
            print("\n👋 Até logo! Obrigado por usar o Alpha Dolar 2.0!\n")
            sys.exit(0)

        elif escolha == "1":
            print("\n🎯 Iniciando modo MANUAL...")
            try:
                from manual import iniciar_modo_manual
                iniciar_modo_manual()
            except ImportError:
                print("❌ Erro: Modo Manual ainda não implementado!")
                input("\nPressione ENTER para voltar ao menu...")

        elif escolha == "2":
            print("\n🤖 Iniciando modo IA SIMPLES...")
            try:
                from ia_simples import iniciar_ia_simples
                iniciar_ia_simples()
            except ImportError:
                print("❌ Erro: Modo IA Simples ainda não implementado!")
                input("\nPressione ENTER para voltar ao menu...")

        elif escolha == "3":
            print("\n🧠 Iniciando modo IA AVANÇADA...")
            try:
                from ia_avancada import iniciar_ia_avancada
                iniciar_ia_avancada()
            except ImportError:
                print("❌ Erro: Modo IA Avançada ainda não implementado!")
                input("\nPressione ENTER para voltar ao menu...")

        else:
            print("\n❌ Opção inválida! Digite um número de 0 a 3.")
            input("\nPressione ENTER para continuar...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Bot interrompido pelo usuário. Até logo!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Erro fatal: {e}")
        sys.exit(1)