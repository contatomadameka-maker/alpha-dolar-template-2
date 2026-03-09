"""
ALPHA DOLAR 2.0 - Trade Executor
Executa trades reais via Deriv API
"""

import asyncio
from typing import Dict, Optional
from datetime import datetime


class TradeExecutor:
    """Executor de trades real via Deriv API"""

    def __init__(self, deriv_client):
        """
        Args:
            deriv_client: Instância de DerivAPI conectada
        """
        self.client = deriv_client
        self.active_contracts = {}
        self.trade_history = []

    async def execute_trade(self, params: Dict) -> Optional[Dict]:
        """
        Executa um trade real

        Args:
            params: {
                'symbol': str,
                'contract_type': str,
                'amount': float,
                'duration': int,
                'duration_unit': str,
                'barrier': int (opcional)
            }

        Returns:
            dict com resultado do trade
        """
        if not self.client.authorized:
            print("❌ Cliente não autorizado!")
            return None

        try:
            # Validações
            if params['amount'] > self.client.balance:
                print(f"❌ Saldo insuficiente! Necessário: ${params['amount']:.2f}, Disponível: ${self.client.balance:.2f}")
                return None

            # Executa compra
            print(f"\n{'='*60}")
            print(f"🎯 EXECUTANDO TRADE REAL")
            print(f"{'='*60}")
            print(f"📊 Mercado: {params['symbol']}")
            print(f"🎲 Tipo: {params['contract_type']}")
            print(f"💰 Stake: ${params['amount']:.2f}")
            print(f"⏱️ Duração: {params['duration']} {params['duration_unit']}")
            if 'barrier' in params and params['barrier'] is not None:
                print(f"🎯 Barreira: {params['barrier']}")
            print(f"{'='*60}\n")

            contract = await self.client.buy_contract(params)

            if contract:
                # Armazena contrato ativo
                contract_id = contract['contract_id']
                self.active_contracts[contract_id] = {
                    'params': params,
                    'contract': contract,
                    'status': 'open',
                    'start_time': datetime.now()
                }

                # Adiciona ao histórico
                self.trade_history.append({
                    'timestamp': datetime.now(),
                    'params': params,
                    'contract': contract,
                    'status': 'executed'
                })

                return contract
            else:
                return None

        except Exception as e:
            print(f"❌ Erro ao executar trade: {e}")
            return None

    async def check_contract_result(self, contract_id: str) -> Optional[Dict]:
        """
        Verifica resultado de um contrato

        Args:
            contract_id: ID do contrato

        Returns:
            dict com resultado ou None se ainda aberto
        """
        try:
            request = {
                "proposal_open_contract": 1,
                "contract_id": contract_id,
                "subscribe": 1
            }

            await self.client.send_request(request)
            response = await self.client.receive_response()

            if "proposal_open_contract" in response:
                contract = response["proposal_open_contract"]

                # Verifica se fechou
                if contract.get("is_sold") == 1:
                    profit = float(contract.get("profit", 0))
                    status = "won" if profit > 0 else "lost"

                    result = {
                        'contract_id': contract_id,
                        'status': status,
                        'profit': profit,
                        'buy_price': float(contract.get("buy_price", 0)),
                        'sell_price': float(contract.get("sell_price", 0)),
                        'exit_tick': contract.get("exit_tick")
                    }

                    # Atualiza contrato
                    if contract_id in self.active_contracts:
                        self.active_contracts[contract_id]['status'] = 'closed'
                        self.active_contracts[contract_id]['result'] = result

                    return result
                else:
                    # Ainda aberto
                    return None

        except Exception as e:
            print(f"❌ Erro ao verificar contrato: {e}")
            return None

    def get_statistics(self) -> Dict:
        """Retorna estatísticas dos trades executados"""
        total = len(self.trade_history)

        if total == 0:
            return {
                'total_trades': 0,
                'wins': 0,
                'losses': 0,
                'win_rate': 0,
                'total_profit': 0
            }

        wins = sum(1 for t in self.trade_history if t.get('result', {}).get('status') == 'won')
        losses = total - wins

        total_profit = sum(t.get('result', {}).get('profit', 0) for t in self.trade_history)

        return {
            'total_trades': total,
            'wins': wins,
            'losses': losses,
            'win_rate': (wins / total * 100) if total > 0 else 0,
            'total_profit': total_profit
        }


if __name__ == "__main__":
    print("TradeExecutor criado com sucesso!")
    print("Use junto com DerivAPI para executar trades reais")