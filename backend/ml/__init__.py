"""
ALPHA DOLAR 2.0 - ML Module
Machine Learning para predição de dígitos
"""

from .historical_data_fetcher import HistoricalDataFetcher, download_multiple_symbols
from .ml_predictor import MLPredictor, prepare_features

__all__ = [
    'HistoricalDataFetcher',
    'download_multiple_symbols',
    'MLPredictor',
    'prepare_features'
]