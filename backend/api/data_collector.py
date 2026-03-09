"""
ALPHA DOLAR 2.0 - Data Collector
Coleta dados históricos para Machine Learning
"""

import asyncio
import json
import csv
from datetime import datetime
from pathlib import Path
from typing import List, Dict


class DataCollector:
    """Coleta e armazena dados históricos de ticks"""

    def __init__(self, data_dir: str = "./data"):
        """
        Args:
            data_dir: Diretório para salvar dados
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

        self.ticks_buffer = []
        self.max_buffer_size = 1000

    def add_tick(self, tick_data: Dict):
        """
        Adiciona tick ao buffer

        Args:
            tick_data: dados do tick {symbol, quote, epoch, etc}
        """
        processed_tick = {
            'timestamp': datetime.now().isoformat(),
            'epoch': tick_data.get('epoch'),
            'symbol': tick_data.get('symbol'),
            'quote': float(tick_data.get('quote', 0)),
            'ask': float(tick_data.get('ask', 0)),
            'bid': float(tick_data.get('bid', 0)),
        }

        # Adiciona dígito
        quote_str = str(processed_tick['quote'])
        last_digit = int(quote_str.replace('.', '')[-1]) if quote_str else 0
        processed_tick['last_digit'] = last_digit
        processed_tick['is_even'] = last_digit % 2 == 0

        self.ticks_buffer.append(processed_tick)

        # Salva se buffer cheio
        if len(self.ticks_buffer) >= self.max_buffer_size:
            self.save_buffer()

    def save_buffer(self, symbol: str = "ticks"):
        """Salva buffer em arquivo"""
        if not self.ticks_buffer:
            return

        filename = self.data_dir / f"{symbol}_{datetime.now().strftime('%Y%m%d')}.csv"

        # Verifica se arquivo existe
        file_exists = filename.exists()

        with open(filename, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'timestamp', 'epoch', 'symbol', 'quote',
                'ask', 'bid', 'last_digit', 'is_even'
            ])

            if not file_exists:
                writer.writeheader()

            writer.writerows(self.ticks_buffer)

        print(f"💾 {len(self.ticks_buffer)} ticks salvos em {filename}")
        self.ticks_buffer = []

    def load_ticks(self, symbol: str, days: int = 1) -> List[Dict]:
        """
        Carrega ticks históricos

        Args:
            symbol: Símbolo do mercado
            days: Número de dias para carregar

        Returns:
            Lista de ticks
        """
        ticks = []

        # Busca arquivos dos últimos N dias
        for day in range(days):
            date_str = datetime.now().strftime('%Y%m%d')
            filename = self.data_dir / f"{symbol}_{date_str}.csv"

            if filename.exists():
                with open(filename, 'r') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        ticks.append(row)

        return ticks

    def get_statistics(self, symbol: str = None) -> Dict:
        """Retorna estatísticas dos dados coletados"""
        if symbol:
            ticks = self.load_ticks(symbol)
        else:
            ticks = self.ticks_buffer

        if not ticks:
            return {
                'total_ticks': 0,
                'even_count': 0,
                'odd_count': 0,
                'digit_distribution': {}
            }

        total = len(ticks)
        even_count = sum(1 for t in ticks if t.get('is_even'))
        odd_count = total - even_count

        # Distribuição de dígitos
        digit_dist = {}
        for i in range(10):
            count = sum(1 for t in ticks if t.get('last_digit') == i)
            digit_dist[i] = {
                'count': count,
                'percentage': (count / total * 100) if total > 0 else 0
            }

        return {
            'total_ticks': total,
            'even_count': even_count,
            'odd_count': odd_count,
            'even_percentage': (even_count / total * 100) if total > 0 else 0,
            'odd_percentage': (odd_count / total * 100) if total > 0 else 0,
            'digit_distribution': digit_dist
        }

    def prepare_for_ml(self, symbol: str, window_size: int = 10) -> tuple:
        """
        Prepara dados para Machine Learning

        Args:
            symbol: Símbolo do mercado
            window_size: Tamanho da janela de observação

        Returns:
            (X, y) onde X são features e y são labels
        """
        ticks = self.load_ticks(symbol)

        if len(ticks) < window_size + 1:
            return [], []

        X = []  # Features
        y = []  # Labels (próximo dígito)

        for i in range(len(ticks) - window_size):
            # Features: últimos N dígitos
            window = [int(t.get('last_digit', 0)) for t in ticks[i:i+window_size]]

            # Label: próximo dígito
            next_digit = int(ticks[i + window_size].get('last_digit', 0))

            X.append(window)
            y.append(next_digit)

        return X, y


if __name__ == "__main__":
    # Teste
    print("=" * 60)
    print("DATA COLLECTOR - TESTE")
    print("=" * 60)

    collector = DataCollector()

    # Simula alguns ticks
    for i in range(20):
        tick = {
            'symbol': 'R_100',
            'quote': 10000 + i * 0.5,
            'epoch': 1234567890 + i,
            'ask': 10000 + i * 0.5 + 0.1,
            'bid': 10000 + i * 0.5 - 0.1
        }
        collector.add_tick(tick)

    # Estatísticas
    stats = collector.get_statistics()
    print(f"\n📊 Estatísticas:")
    print(f"   Total: {stats['total_ticks']} ticks")
    print(f"   Pares: {stats['even_count']} ({stats['even_percentage']:.1f}%)")
    print(f"   Ímpares: {stats['odd_count']} ({stats['odd_percentage']:.1f}%)")

    print(f"\n📊 Distribuição de dígitos:")
    for digit, info in stats['digit_distribution'].items():
        print(f"   {digit}: {info['count']} ({info['percentage']:.1f}%)")

    # Salva
    collector.save_buffer("R_100")

    print("\n✅ Teste concluído!")