"""
ALPHA DOLAR 2.0 - Historical Data Fetcher
Baixa dados históricos da Deriv para treinamento de ML
"""

import asyncio
import json
import csv
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict


class HistoricalDataFetcher:
    """Baixa dados históricos da Deriv API"""

    def __init__(self, data_dir: str = "./data/historical"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

    async def fetch_ticks_history(self, symbol: str, count: int = 5000) -> List[Dict]:
        """
        Baixa histórico de ticks

        Args:
            symbol: Símbolo do mercado (R_100, R_50, etc)
            count: Quantidade de ticks (máx 5000)

        Returns:
            Lista de ticks
        """
        try:
            import sys
            import os
            sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

            from api.deriv_api import DerivAPI

            print(f"📊 Baixando {count} ticks de {symbol}...")

            # Conecta sem autenticação (dados públicos)
            client = DerivAPI(api_token=None, is_demo=True)
            await client.connect()

            # Requisita histórico
            request = {
                "ticks_history": symbol,
                "count": count,
                "end": "latest",
                "style": "ticks"
            }

            await client.send_request(request)
            response = await client.receive_response()

            if "history" in response:
                history = response["history"]
                ticks = []

                for i, (timestamp, price) in enumerate(zip(history["times"], history["prices"])):
                    tick = {
                        'timestamp': timestamp,
                        'datetime': datetime.fromtimestamp(timestamp),
                        'symbol': symbol,
                        'price': float(price)
                    }

                    # Extrai dígito
                    price_str = str(tick['price'])
                    last_digit = int(price_str.replace('.', '')[-1])
                    tick['last_digit'] = last_digit
                    tick['is_even'] = last_digit % 2 == 0

                    ticks.append(tick)

                await client.disconnect()

                print(f"✅ {len(ticks)} ticks baixados!")
                return ticks
            else:
                print(f"❌ Erro: {response}")
                return []

        except Exception as e:
            print(f"❌ Erro ao baixar dados: {e}")
            return []

    def save_to_csv(self, ticks: List[Dict], symbol: str):
        """Salva ticks em CSV"""
        if not ticks:
            return

        filename = self.data_dir / f"{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        with open(filename, 'w', newline='') as f:
            fieldnames = ['timestamp', 'datetime', 'symbol', 'price', 'last_digit', 'is_even']
            writer = csv.DictWriter(f, fieldnames=fieldnames)

            writer.writeheader()
            writer.writerows(ticks)

        print(f"💾 Dados salvos em: {filename}")
        return filename

    def load_from_csv(self, filename: str) -> List[Dict]:
        """Carrega ticks de CSV"""
        ticks = []

        with open(filename, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                row['timestamp'] = int(row['timestamp'])
                row['price'] = float(row['price'])
                row['last_digit'] = int(row['last_digit'])
                row['is_even'] = row['is_even'] == 'True'
                ticks.append(row)

        return ticks

    def prepare_training_data(self, ticks: List[Dict], window_size: int = 10,
                            target: str = 'digit') -> tuple:
        """
        Prepara dados para treinamento

        Args:
            ticks: Lista de ticks
            window_size: Tamanho da janela de observação
            target: 'digit' (próximo dígito) ou 'even' (par/ímpar)

        Returns:
            (X, y) features e labels
        """
        if len(ticks) < window_size + 1:
            return [], []

        X = []  # Features
        y = []  # Labels

        for i in range(len(ticks) - window_size):
            # Features: últimos N dígitos
            window = [t['last_digit'] for t in ticks[i:i+window_size]]

            # Adiciona features extras
            features = window.copy()

            # Contagem de pares/ímpares na janela
            even_count = sum(1 for d in window if d % 2 == 0)
            odd_count = len(window) - even_count
            features.append(even_count)
            features.append(odd_count)

            # Últimos 3 dígitos (mais peso)
            features.extend(window[-3:])

            # Label: próximo valor
            if target == 'digit':
                label = ticks[i + window_size]['last_digit']
            else:  # even
                label = 1 if ticks[i + window_size]['is_even'] else 0

            X.append(features)
            y.append(label)

        return X, y

    def get_statistics(self, ticks: List[Dict]) -> Dict:
        """Estatísticas dos dados"""
        if not ticks:
            return {}

        digits = [t['last_digit'] for t in ticks]

        # Distribuição
        digit_dist = {}
        for i in range(10):
            count = digits.count(i)
            digit_dist[i] = {
                'count': count,
                'percentage': count / len(digits) * 100
            }

        # Pares vs ímpares
        even_count = sum(1 for t in ticks if t['is_even'])
        odd_count = len(ticks) - even_count

        # Sequências
        max_even_seq = 0
        max_odd_seq = 0
        current_even_seq = 0
        current_odd_seq = 0

        for tick in ticks:
            if tick['is_even']:
                current_even_seq += 1
                current_odd_seq = 0
                max_even_seq = max(max_even_seq, current_even_seq)
            else:
                current_odd_seq += 1
                current_even_seq = 0
                max_odd_seq = max(max_odd_seq, current_odd_seq)

        return {
            'total_ticks': len(ticks),
            'even_count': even_count,
            'odd_count': odd_count,
            'even_percentage': even_count / len(ticks) * 100,
            'odd_percentage': odd_count / len(ticks) * 100,
            'digit_distribution': digit_dist,
            'max_even_sequence': max_even_seq,
            'max_odd_sequence': max_odd_seq,
            'start_time': ticks[0]['datetime'],
            'end_time': ticks[-1]['datetime']
        }


async def download_multiple_symbols(symbols: List[str], count: int = 5000):
    """Baixa dados de múltiplos símbolos"""
    fetcher = HistoricalDataFetcher()

    print("=" * 60)
    print("BAIXANDO DADOS HISTÓRICOS")
    print("=" * 60)

    for symbol in symbols:
        print(f"\n📊 {symbol}:")
        ticks = await fetcher.fetch_ticks_history(symbol, count)

        if ticks:
            # Salva
            filename = fetcher.save_to_csv(ticks, symbol)

            # Estatísticas
            stats = fetcher.get_statistics(ticks)
            print(f"\n📈 Estatísticas:")
            print(f"   Total: {stats['total_ticks']} ticks")
            print(f"   Pares: {stats['even_count']} ({stats['even_percentage']:.1f}%)")
            print(f"   Ímpares: {stats['odd_count']} ({stats['odd_percentage']:.1f}%)")
            print(f"   Período: {stats['start_time']} até {stats['end_time']}")

        # Aguarda 1s entre requisições
        await asyncio.sleep(1)

    print("\n✅ Download completo!")


if __name__ == "__main__":
    # Símbolos para baixar
    symbols = [
        'R_100',   # Volatility 100
        'R_50',    # Volatility 50
        'R_25',    # Volatility 25
    ]

    # Baixa dados
    asyncio.run(download_multiple_symbols(symbols, count=5000))