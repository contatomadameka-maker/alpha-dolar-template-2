"""
ALPHA DOLAR 2.0 - Bot Manual
Permite execução manual de trades com interface profissional
"""

import sys
import os
from datetime import datetime

# Adiciona o diretório pai ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from markets import (
    get_all_markets,
    get_markets_by_category,
    MARKET_CATEGORIES,
    get_all_contract_types,
    get_contracts_by_category,
    CONTRACT_CATEGORIES,
    DURATIONS
)


class ManualBot:
    """Bot para execução manual de trades"""

    def __init__(self):
        self.name = "ALPHA DOLAR 2.0 - BOT MANUAL"
        self.version = "1.0.0"

        # Configurações do trade
        self.selected_market = None
        self.selected_contract = None
        self.selected_duration = {"value": 1, "unit": "t"}
        self.stake = 1.00
        self.barrier = None

    def print_header(self):
        """Exibe cabeçalho"""
        print("\n" + "=" * 70)
        print(f"🎮 {self.name} v{self.version}")
        print("=" * 70)
        print("📝 MODO: Manual - Você escolhe cada trade!")
        print("=" * 70 + "\n")

    def select_market(self):
        """Interface para selecionar mercado"""
        print("\n" + "=" * 70)
        print("📊 SELECIONE O MERCADO")
        print("=" * 70)

        # Exibe categorias
        for idx, category in enumerate(MARKET_CATEGORIES, 1):
            market_count = len(get_markets_by_category(category["key"]))
            print(f"{idx}. {category['icon']} {category['name']} ({market_count} mercados)")

        print("0. ❌ Voltar")

        try:
            choice = int(input("\n👉 Escolha uma categoria: "))

            if choice == 0:
                return False

            if 1 <= choice <= len(MARKET_CATEGORIES):
                category = MARKET_CATEGORIES[choice - 1]
                return self.select_market_from_category(category)
            else:
                print("❌ Opção inválida!")
                return self.select_market()

        except ValueError:
            print("❌ Digite um número válido!")
            return self.select_market()

    def select_market_from_category(self, category):
        """Seleciona mercado de uma categoria"""
        markets = get_markets_by_category(category["key"])

        print(f"\n{category['icon']} {category['name']}")
        print("=" * 70)

        for idx, market in enumerate(markets, 1):
            tick_info = f"({market['tick']})" if market.get('tick') else ""
            print(f"{idx}. {market['icon']} {market['name']} {tick_info}")

        print("0. ⬅️ Voltar")

        try:
            choice = int(input("\n👉 Escolha um mercado: "))

            if choice == 0:
                return self.select_market()

            if 1 <= choice <= len(markets):
                self.selected_market = markets[choice - 1]
                print(f"\n✅ Mercado selecionado: {self.selected_market['icon']} {self.selected_market['name']}")
                return True
            else:
                print("❌ Opção inválida!")
                return self.select_market_from_category(category)

        except ValueError:
            print("❌ Digite um número válido!")
            return self.select_market_from_category(category)

    def select_contract_type(self):
        """Interface para selecionar tipo de contrato"""
        print("\n" + "=" * 70)
        print("🎯 SELECIONE O TIPO DE NEGOCIAÇÃO")
        print("=" * 70)

        for idx, category in enumerate(CONTRACT_CATEGORIES, 1):
            contract_count = len(get_contracts_by_category(category["key"]))
            print(f"{idx}. {category['icon']} {category['name']} ({contract_count} tipos)")

        print("0. ❌ Voltar")

        try:
            choice = int(input("\n👉 Escolha uma categoria: "))

            if choice == 0:
                return False

            if 1 <= choice <= len(CONTRACT_CATEGORIES):
                category = CONTRACT_CATEGORIES[choice - 1]
                return self.select_contract_from_category(category)
            else:
                print("❌ Opção inválida!")
                return self.select_contract_type()

        except ValueError:
            print("❌ Digite um número válido!")
            return self.select_contract_type()

    def select_contract_from_category(self, category):
        """Seleciona contrato de uma categoria"""
        contracts = get_contracts_by_category(category["key"])

        print(f"\n{category['icon']} {category['name']}")
        print("=" * 70)

        for idx, contract in enumerate(contracts, 1):
            barrier_info = "🎯" if contract.get("requires_barrier") else "✅"
            print(f"{idx}. {contract['icon']} {contract['name']} {barrier_info}")
            print(f"    💡 {contract['description']}")

        print("0. ⬅️ Voltar")

        try:
            choice = int(input("\n👉 Escolha um tipo: "))

            if choice == 0:
                return self.select_contract_type()

            if 1 <= choice <= len(contracts):
                self.selected_contract = contracts[choice - 1]
                print(f"\n✅ Tipo selecionado: {self.selected_contract['icon']} {self.selected_contract['name']}")

                # Se requer barreira, solicita
                if self.selected_contract.get("requires_barrier"):
                    return self.set_barrier()

                return True
            else:
                print("❌ Opção inválida!")
                return self.select_contract_from_category(category)

        except ValueError:
            print("❌ Digite um número válido!")
            return self.select_contract_from_category(category)

    def set_barrier(self):
        """Define a barreira"""
        barrier_range = self.selected_contract.get("barrier_range", [0, 9])

        print(f"\n🎯 DEFINA A BARREIRA")
        print(f"📊 {self.selected_contract['description']}")
        print(f"📏 Intervalo permitido: {barrier_range[0]} - {barrier_range[1]}")

        try:
            barrier = int(input(f"\n👉 Digite a barreira ({barrier_range[0]}-{barrier_range[1]}): "))

            if barrier_range[0] <= barrier <= barrier_range[1]:
                self.barrier = barrier
                print(f"✅ Barreira definida: {barrier}")
                return True
            else:
                print(f"❌ Barreira deve estar entre {barrier_range[0]} e {barrier_range[1]}!")
                return self.set_barrier()

        except ValueError:
            print("❌ Digite um número válido!")
            return self.set_barrier()

    def set_duration(self):
        """Define duração do trade"""
        print("\n" + "=" * 70)
        print("⏱️ SELECIONE A DURAÇÃO")
        print("=" * 70)

        duration_types = list(DURATIONS.items())

        for idx, (key, duration) in enumerate(duration_types, 1):
            print(f"{idx}. {duration['icon']} {duration['name']}")

        print("0. ⬅️ Voltar")

        try:
            choice = int(input("\n👉 Escolha o tipo de duração: "))

            if choice == 0:
                return False

            if 1 <= choice <= len(duration_types):
                duration_key, duration_data = duration_types[choice - 1]
                return self.set_duration_value(duration_data)
            else:
                print("❌ Opção inválida!")
                return self.set_duration()

        except ValueError:
            print("❌ Digite um número válido!")
            return self.set_duration()

    def set_duration_value(self, duration_data):
        """Define valor da duração"""
        print(f"\n⏱️ {duration_data['name']}")
        print("Valores disponíveis:", ", ".join(map(str, duration_data['values'])))

        try:
            value = int(input(f"\n👉 Digite a duração: "))

            if value in duration_data['values']:
                self.selected_duration = {
                    "value": value,
                    "unit": duration_data['unit'],
                    "name": duration_data['name']
                }
                print(f"✅ Duração: {value} {duration_data['name']}")
                return True
            else:
                print("❌ Valor não está na lista!")
                return self.set_duration_value(duration_data)

        except ValueError:
            print("❌ Digite um número válido!")
            return self.set_duration_value(duration_data)

    def set_stake(self):
        """Define valor do stake"""
        print(f"\n💰 DEFINA O VALOR DO STAKE")
        print(f"Atual: ${self.stake:.2f}")

        try:
            stake = float(input("\n👉 Digite o valor (USD): $"))

            if stake > 0:
                self.stake = stake
                print(f"✅ Stake definido: ${stake:.2f}")
                return True
            else:
                print("❌ Valor deve ser maior que 0!")
                return self.set_stake()

        except ValueError:
            print("❌ Digite um valor válido!")
            return self.set_stake()

    def show_summary(self):
        """Exibe resumo do trade"""
        print("\n" + "=" * 70)
        print("📋 RESUMO DO TRADE")
        print("=" * 70)

        if self.selected_market:
            print(f"📊 Mercado: {self.selected_market['icon']} {self.selected_market['name']}")
            print(f"   Symbol: {self.selected_market['symbol']}")

        if self.selected_contract:
            print(f"\n🎯 Tipo: {self.selected_contract['icon']} {self.selected_contract['name']}")
            print(f"   {self.selected_contract['description']}")

            if self.barrier is not None:
                print(f"   Barreira: {self.barrier}")

        if self.selected_duration:
            print(f"\n⏱️ Duração: {self.selected_duration['value']} {self.selected_duration.get('name', 'ticks')}")

        print(f"\n💰 Stake: ${self.stake:.2f}")

        print("=" * 70)

    def execute_trade(self):
        """Executa o trade (simulação)"""
        print("\n🚀 EXECUTANDO TRADE...")

        # Monta parâmetros
        params = {
            "symbol": self.selected_market['symbol'],
            "contract_type": self.selected_contract['type'],
            "duration": self.selected_duration['value'],
            "duration_unit": self.selected_duration['unit'],
            "amount": self.stake,
            "basis": "stake",
            "currency": "USD"
        }

        if self.barrier is not None:
            params["barrier"] = self.barrier

        print("\n📦 Parâmetros do Trade:")
        for key, value in params.items():
            print(f"   {key}: {value}")

        print("\n✅ Trade enviado com sucesso!")
        print("💡 Em produção, aqui seria feita a chamada real para a API Deriv")

        return params

    def run(self):
        """Loop principal"""
        self.print_header()

        while True:
            print("\n" + "=" * 70)
            print("🎮 MENU PRINCIPAL")
            print("=" * 70)
            print("1. 📊 Selecionar Mercado")
            print("2. 🎯 Selecionar Tipo de Negociação")
            print("3. ⏱️ Definir Duração")
            print("4. 💰 Definir Stake")
            print("5. 📋 Ver Resumo")
            print("6. 🚀 EXECUTAR TRADE")
            print("0. ❌ Sair")

            try:
                choice = int(input("\n👉 Escolha uma opção: "))

                if choice == 0:
                    print("\n👋 Até logo!")
                    break
                elif choice == 1:
                    self.select_market()
                elif choice == 2:
                    self.select_contract_type()
                elif choice == 3:
                    self.set_duration()
                elif choice == 4:
                    self.set_stake()
                elif choice == 5:
                    self.show_summary()
                elif choice == 6:
                    if not self.selected_market:
                        print("❌ Selecione um mercado primeiro!")
                    elif not self.selected_contract:
                        print("❌ Selecione um tipo de negociação primeiro!")
                    else:
                        self.show_summary()
                        confirm = input("\n❓ Confirmar trade? (s/n): ")
                        if confirm.lower() == 's':
                            self.execute_trade()
                else:
                    print("❌ Opção inválida!")

            except ValueError:
                print("❌ Digite um número válido!")
            except KeyboardInterrupt:
                print("\n\n👋 Até logo!")
                break


if __name__ == "__main__":
    bot = ManualBot()
    bot.run()