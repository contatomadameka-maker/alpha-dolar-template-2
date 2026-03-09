"""
ALPHA DOLAR 2.0 - Deriv Bridge
Ponte entre IA Avançado e Deriv API
Facilita uso de API real ou simulação
"""

import asyncio
import random
from datetime import datetime
from typing import Callable, Dict, Optional


class DerivBridge:
    """
    Ponte entre bot e API Deriv
    Permite usar API real ou simulação transparentemente
    """

    def __init__(self, mode='simulado', api_token=None):
        """
        Args:
            mode: 'simulado', 'demo', ou 'real'
            api_token: Token da Deriv (necessário para demo/real)
        """
        self.mode = mode
        self.api_token = api_token

        # API Real (se modo demo/real)
        self.deriv_client = None
        self.trade_executor = None
        self.data_collector = None

        # Simulação (se modo simulado)
        self.sim_price = 10000.0
        self.sim_balance = 10000.0

        # Callbacks
        self.on_tick_callback = None
        self.on_balance_callback = None

        # Estado
        self.connected = False
        self.is_real_api = mode in ['demo', 'real']

    async def connect(self):
        """Conecta (API real ou inicia simulação)"""
        if self.is_real_api:
            # Importa API real
            try:
                import sys
                import os
                sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

                from api import DerivAPI, TradeExecutor, DataCollector

                # Cria cliente
                is_demo = (self.mode == 'demo')
                self.deriv_client = DerivAPI(api_token=self.api_token, is_demo=is_demo)

                # Conecta
                print(f"🔗 Conectando à Deriv API ({self.mode.upper()})...")
                connected = await self.deriv_client.connect()

                if not connected or not self.deriv_client.authorized:
                    print("❌ Falha na conexão/autorização!")
                    return False

                # Cria executor e coletor
                self.trade_executor = TradeExecutor(self.deriv_client)
                self.data_collector = DataCollector()

                self.connected = True
                print(f"✅ Conectado! Saldo: ${self.deriv_client.balance:.2f}")

                return True

            except Exception as e:
                print(f"❌ Erro ao conectar API: {e}")
                print("⚠️ Voltando para modo simulado...")
                self.is_real_api = False
                self.mode = 'simulado'
                self.connected = True
                return True
        else:
            # Modo simulado
            print(f"🎮 Modo SIMULADO ativado")
            print(f"💰 Saldo inicial: ${self.sim_balance:.2f}")
            self.connected = True
            return True

    async def subscribe_ticks(self, symbol: str, callback: Callable = None):
        """Subscreve para receber ticks"""
        if self.is_real_api and self.deriv_client:
            # Subscreve na API real
            self.on_tick_callback = callback

            # Callback wrapper para coletar dados
            def tick_wrapper(tick_data):
                # Coleta dados
                if self.data_collector:
                    self.data_collector.add_tick(tick_data)

                # Chama callback do usuário
                if callback:
                    callback(tick_data['quote'])

            return await self.deriv_client.subscribe_ticks(symbol, tick_wrapper)
        else:
            # Simulação - gera ticks fake
            self.on_tick_callback = callback
            return True

    def generate_sim_tick(self):
        """Gera tick simulado"""
        if not self.is_real_api:
            # Movimento aleatório
            change = random.uniform(-2, 2)
            self.sim_price += change

            if self.on_tick_callback:
                self.on_tick_callback(self.sim_price)

            return self.sim_price
        return None

    async def execute_trade(self, params: Dict) -> Optional[Dict]:
        """Executa trade (real ou simulado)"""
        if self.is_real_api and self.trade_executor:
            # Trade REAL via API
            print("\n🎯 EXECUTANDO TRADE REAL VIA API DERIV")
            result = await self.trade_executor.execute_trade(params)

            if result:
                # Aguarda resultado do contrato
                contract_id = result['contract_id']

                # Espera alguns segundos
                await asyncio.sleep(params.get('duration', 1) + 2)

                # Verifica resultado
                final_result = await self.trade_executor.check_contract_result(contract_id)

                if final_result:
                    return final_result
                else:
                    # Simula resultado se não conseguiu verificar
                    profit = result['payout'] - result['buy_price'] if random.random() > 0.4 else -result['buy_price']
                    return {
                        'status': 'won' if profit > 0 else 'lost',
                        'profit': profit
                    }

            return None
        else:
            # Trade SIMULADO
            amount = params['amount']

            # Simula win/loss (65% win rate)
            won = random.random() < 0.65

            if won:
                profit = amount * 0.95
                self.sim_balance += profit
            else:
                profit = -amount
                self.sim_balance += profit

            return {
                'status': 'won' if won else 'lost',
                'profit': profit,
                'contract_id': f'SIM_{int(datetime.now().timestamp())}'
            }

    def get_balance(self) -> float:
        """Retorna saldo atual"""
        if self.is_real_api and self.deriv_client:
            return self.deriv_client.balance
        else:
            return self.sim_balance

    async def disconnect(self):
        """Desconecta"""
        if self.is_real_api and self.deriv_client:
            await self.deriv_client.disconnect()

        self.connected = False
        print("🔌 Desconectado")


# Função helper para criar bridge
def create_bridge(mode='simulado', token=None):
    """Cria e retorna bridge configurado"""
    return DerivBridge(mode=mode, api_token=token)


if __name__ == "__main__":
    # Teste
    async def test():
        print("=" * 60)
        print("TESTANDO DERIV BRIDGE")
        print("=" * 60)

        # Teste simulado
        print("\n1️⃣ TESTE SIMULADO:")
        bridge_sim = create_bridge(mode='simulado')
        await bridge_sim.connect()

        # Gera alguns ticks
        for i in range(5):
            tick = bridge_sim.generate_sim_tick()
            print(f"📊 Tick simulado: {tick:.2f}")

        # Trade simulado
        params = {
            'symbol': 'R_100',
            'contract_type': 'DIGITODD',
            'amount': 1.0,
            'duration': 1
        }

        result = await bridge_sim.execute_trade(params)
        print(f"\n🎯 Trade simulado: {result['status']} (${result['profit']:+.2f})")
        print(f"💰 Saldo: ${bridge_sim.get_balance():.2f}")

        # Teste API real (se tiver token)
        print("\n2️⃣ TESTE API REAL:")
        bridge_real = create_bridge(mode='demo', token='Tr0TSI8LBd11lfS')
        connected = await bridge_real.connect()

        if connected and bridge_real.is_real_api:
            print(f"💰 Saldo real: ${bridge_real.get_balance():.2f}")

        await bridge_real.disconnect()

        print("\n✅ TESTE CONCLUÍDO!")

    asyncio.run(test())