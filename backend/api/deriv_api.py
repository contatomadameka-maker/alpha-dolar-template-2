"""
ALPHA DOLAR 2.0 - Deriv API Client
Cliente WebSocket para conexão real com Deriv API
"""

import asyncio
import json
import websockets
from typing import Callable, Dict, Optional
from datetime import datetime


class DerivAPI:
    """Cliente para API Deriv via WebSocket"""

    def __init__(self, api_token: str = None, is_demo: bool = True):
        """
        Args:
            api_token: Token de API da Deriv
            is_demo: True para conta demo, False para real
        """
        self.api_token = api_token
        self.is_demo = is_demo

        # Endpoints
        if is_demo:
            self.endpoint = "wss://ws.derivws.com/websockets/v3?app_id=1089"
        else:
            self.endpoint = "wss://ws.derivws.com/websockets/v3?app_id=1089"

        self.websocket = None
        self.connected = False
        self.authorized = False

        # Callbacks
        self.tick_callback = None
        self.trade_callback = None
        self.balance_callback = None

        # Dados
        self.balance = 0
        self.account_info = {}
        self.active_subscriptions = {}

    async def connect(self):
        """Conecta ao WebSocket"""
        try:
            print("🔗 Conectando à Deriv API...")
            self.websocket = await websockets.connect(
                self.endpoint,
                ping_interval=30,
                ping_timeout=10
            )
            self.connected = True
            print("✅ Conectado!")

            # Autoriza se tiver token
            if self.api_token:
                await self.authorize()

            return True

        except Exception as e:
            print(f"❌ Erro ao conectar: {e}")
            self.connected = False
            return False

    async def authorize(self):
        """Autoriza com API token"""
        if not self.api_token:
            print("⚠️ Token não fornecido")
            return False

        try:
            print("🔐 Autorizando...")
            request = {
                "authorize": self.api_token
            }

            await self.send_request(request)
            response = await self.receive_response()

            if "authorize" in response:
                self.authorized = True
                self.account_info = response["authorize"]
                self.balance = float(response["authorize"].get("balance", 0))

                account_type = "DEMO" if self.is_demo else "REAL"
                print(f"✅ Autorizado! Conta: {account_type}")
                print(f"💰 Saldo: ${self.balance:.2f}")
                print(f"👤 ID: {self.account_info.get('loginid', 'N/A')}")

                return True
            else:
                print(f"❌ Falha na autorização: {response}")
                return False

        except Exception as e:
            print(f"❌ Erro na autorização: {e}")
            return False

    async def send_request(self, request: Dict):
        """Envia requisição ao WebSocket"""
        if not self.connected or not self.websocket:
            raise Exception("WebSocket não conectado")

        await self.websocket.send(json.dumps(request))

    async def receive_response(self) -> Dict:
        """Recebe resposta do WebSocket"""
        if not self.connected or not self.websocket:
            raise Exception("WebSocket não conectado")

        response = await self.websocket.recv()
        return json.loads(response)

    async def subscribe_ticks(self, symbol: str, callback: Callable = None):
        """
        Subscreve para receber ticks em tempo real

        Args:
            symbol: Símbolo do mercado (ex: R_100, CRASH500, frxEURUSD)
            callback: Função chamada a cada tick recebido
        """
        try:
            print(f"📊 Subscrevendo ticks de {symbol}...")

            request = {
                "ticks": symbol,
                "subscribe": 1
            }

            await self.send_request(request)
            response = await self.receive_response()

            if "tick" in response:
                subscription_id = response.get("subscription", {}).get("id")
                self.active_subscriptions[symbol] = subscription_id

                if callback:
                    self.tick_callback = callback

                print(f"✅ Subscrito! ID: {subscription_id}")
                return True
            else:
                print(f"❌ Falha ao subscrever: {response}")
                return False

        except Exception as e:
            print(f"❌ Erro ao subscrever: {e}")
            return False

    async def unsubscribe_ticks(self, symbol: str):
        """Remove subscrição de ticks"""
        if symbol in self.active_subscriptions:
            subscription_id = self.active_subscriptions[symbol]

            request = {
                "forget": subscription_id
            }

            await self.send_request(request)
            del self.active_subscriptions[symbol]
            print(f"✅ Subscrição removida: {symbol}")

    async def get_balance(self):
        """Obtém saldo atual da conta"""
        try:
            request = {
                "balance": 1,
                "subscribe": 1
            }

            await self.send_request(request)
            response = await self.receive_response()

            if "balance" in response:
                self.balance = float(response["balance"]["balance"])

                if self.balance_callback:
                    self.balance_callback(self.balance)

                return self.balance

        except Exception as e:
            print(f"❌ Erro ao obter saldo: {e}")
            return None

    async def buy_contract(self, params: Dict) -> Dict:
        """
        Compra um contrato

        Args:
            params: {
                'contract_type': str (ex: 'DIGITODD', 'CALL'),
                'symbol': str (ex: 'R_100'),
                'amount': float,
                'duration': int,
                'duration_unit': str ('t', 's', 'm', 'h', 'd'),
                'barrier': str (opcional, para DIGITOVER/UNDER)
            }

        Returns:
            dict com informações do contrato ou None se falhar
        """
        if not self.authorized:
            print("❌ Não autorizado! Faça login primeiro.")
            return None

        try:
            # Monta proposta
            proposal_request = {
                "proposal": 1,
                "amount": params['amount'],
                "basis": "stake",
                "contract_type": params['contract_type'],
                "currency": "USD",
                "duration": params['duration'],
                "duration_unit": params['duration_unit'],
                "symbol": params['symbol']
            }

            # Adiciona barreira se necessário
            if 'barrier' in params and params['barrier'] is not None:
                proposal_request["barrier"] = str(params['barrier'])

            # Obter proposta
            print(f"📝 Obtendo proposta...")
            await self.send_request(proposal_request)
            proposal_response = await self.receive_response()

            if "proposal" not in proposal_response:
                print(f"❌ Erro na proposta: {proposal_response}")
                return None

            proposal_id = proposal_response["proposal"]["id"]
            payout = proposal_response["proposal"]["payout"]

            print(f"💰 Proposta aceita! Payout: ${payout:.2f}")

            # Comprar contrato
            buy_request = {
                "buy": proposal_id,
                "price": params['amount']
            }

            print(f"🎯 Comprando contrato...")
            await self.send_request(buy_request)
            buy_response = await self.receive_response()

            if "buy" in buy_response:
                contract = buy_response["buy"]

                print(f"✅ Contrato comprado!")
                print(f"   ID: {contract['contract_id']}")
                print(f"   Stake: ${contract['buy_price']:.2f}")
                print(f"   Payout: ${contract['payout']:.2f}")

                return {
                    'contract_id': contract['contract_id'],
                    'buy_price': float(contract['buy_price']),
                    'payout': float(contract['payout']),
                    'start_time': contract.get('start_time'),
                    'purchase_time': contract.get('purchase_time')
                }
            else:
                print(f"❌ Erro ao comprar: {buy_response}")
                return None

        except Exception as e:
            print(f"❌ Erro ao executar trade: {e}")
            return None

    async def listen(self):
        """Loop principal para receber mensagens"""
        if not self.connected:
            print("❌ WebSocket não conectado")
            return

        print("👂 Ouvindo mensagens...")

        try:
            while self.connected:
                response = await self.receive_response()

                # Tick recebido
                if "tick" in response:
                    tick_data = response["tick"]

                    if self.tick_callback:
                        self.tick_callback(tick_data)

                # Atualização de saldo
                elif "balance" in response:
                    self.balance = float(response["balance"]["balance"])

                    if self.balance_callback:
                        self.balance_callback(self.balance)

                # Erro
                elif "error" in response:
                    print(f"⚠️ Erro: {response['error']['message']}")

        except websockets.exceptions.ConnectionClosed:
            print("🔌 Conexão fechada")
            self.connected = False
        except Exception as e:
            print(f"❌ Erro no listener: {e}")
            self.connected = False

    async def disconnect(self):
        """Desconecta do WebSocket"""
        if self.websocket:
            await self.websocket.close()
            self.connected = False
            print("🔌 Desconectado")


# Função helper para uso síncrono
def create_deriv_client(api_token: str = None, is_demo: bool = True):
    """Cria e retorna cliente Deriv"""
    return DerivAPI(api_token=api_token, is_demo=is_demo)


if __name__ == "__main__":
    # Teste
    async def test():
        print("=" * 60)
        print("TESTE DE CONEXÃO COM DERIV API")
        print("=" * 60)

        # Primeiro testa conexão SEM token
        print("\n1️⃣ TESTANDO CONEXÃO (sem autenticação)...")
        client_no_auth = DerivAPI(api_token=None, is_demo=True)
        connected = await client_no_auth.connect()

        if not connected:
            print("❌ Falha ao conectar!")
            return

        print("✅ Conexão OK!")

        # Callback para ticks
        tick_count = [0]
        def on_tick(tick):
            tick_count[0] += 1
            if tick_count[0] <= 3:
                print(f"📊 Tick #{tick_count[0]}: {tick['symbol']} = {tick['quote']}")

        # Subscreve ticks SEM autenticação
        print("\n2️⃣ TESTANDO STREAM DE TICKS (sem autenticação)...")
        await client_no_auth.subscribe_ticks("R_100", on_tick)

        # Escuta por 5 segundos
        await asyncio.sleep(5)

        print(f"\n✅ Recebeu {tick_count[0]} ticks com sucesso!")

        await client_no_auth.disconnect()

        # Agora testa COM token
        print("\n" + "=" * 60)
        print("3️⃣ TESTANDO AUTENTICAÇÃO COM TOKEN...")
        print("=" * 60)

        # Token DEMO
        token = "AGTuSNe2ab2LHAK"

        client = DerivAPI(api_token=token, is_demo=True)

        # Conecta
        connected = await client.connect()

        if not connected or not client.authorized:
            print("\n⚠️ ATENÇÃO:")
            print("   O token pode estar expirado ou inválido.")
            print("   Gere um novo token em: https://app.deriv.com/account/api-token")
            print("   Permissões necessárias: Read + Trade")
            return

        # Pega saldo
        balance = await client.get_balance()
        if balance is not None:
            print(f"\n💰 Saldo: ${balance:.2f}")
        else:
            print("\n⚠️ Não foi possível obter saldo")

        # Desconecta
        await client.disconnect()

        print("\n✅ TESTE CONCLUÍDO!")

    # Roda teste
    asyncio.run(test())