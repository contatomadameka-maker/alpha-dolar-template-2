"""
ALPHA DOLAR 2.0 - Treinar Modelo ML
Script para baixar dados e treinar modelo
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ml import HistoricalDataFetcher, MLPredictor


async def main():
    print("=" * 60)
    print("🧠 ALPHA DOLAR 2.0 - TREINAMENTO DE ML")
    print("=" * 60)

    # Símbolos para baixar
    symbols = ['R_100', 'R_50', 'R_25']
    count = 5000

    fetcher = HistoricalDataFetcher()
    all_ticks = []

    # Baixa dados de cada símbolo
    for symbol in symbols:
        print(f"\n📊 Baixando dados de {symbol}...")
        ticks = await fetcher.fetch_ticks_history(symbol, count)

        if ticks:
            # Salva CSV
            filename = fetcher.save_to_csv(ticks, symbol)

            # Estatísticas
            stats = fetcher.get_statistics(ticks)
            print(f"✅ {stats['total_ticks']} ticks")
            print(f"   Pares: {stats['even_percentage']:.1f}%")
            print(f"   Ímpares: {stats['odd_percentage']:.1f}%")

            all_ticks.extend(ticks)

        await asyncio.sleep(1)

    if not all_ticks:
        print("\n❌ Nenhum dado baixado!")
        return

    print(f"\n📊 Total: {len(all_ticks)} ticks de todos os mercados")

    # Prepara dados para treinamento
    print("\n🔧 Preparando dados para ML...")
    X, y = fetcher.prepare_training_data(all_ticks, window_size=10, target='even')

    print(f"✅ {len(X)} amostras preparadas")

    # Treina Random Forest
    print("\n🌲 Treinando Random Forest...")
    rf_predictor = MLPredictor(model_type='random_forest')
    rf_accuracy = rf_predictor.train(X, y, test_size=0.2)

    if rf_accuracy > 0:
        # Salva modelo
        rf_predictor.save('models/rf_predictor.pkl')

    # Treina XGBoost (opcional)
    try:
        print("\n🚀 Treinando XGBoost...")
        xgb_predictor = MLPredictor(model_type='xgboost')
        xgb_accuracy = xgb_predictor.train(X, y, test_size=0.2)

        if xgb_accuracy > 0:
            xgb_predictor.save('models/xgb_predictor.pkl')

        # Compara
        print("\n📊 COMPARAÇÃO:")
        print(f"   Random Forest: {rf_accuracy:.2%}")
        print(f"   XGBoost: {xgb_accuracy:.2%}")

        if xgb_accuracy > rf_accuracy:
            print(f"\n✅ XGBoost é melhor! (+{(xgb_accuracy - rf_accuracy):.2%})")
        else:
            print(f"\n✅ Random Forest é melhor!")

    except ImportError:
        print("\n⚠️ XGBoost não instalado. Só Random Forest foi treinado.")

    print("\n✅ TREINAMENTO COMPLETO!")
    print(f"💾 Modelos salvos em: models/")


if __name__ == "__main__":
    asyncio.run(main())