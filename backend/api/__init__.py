"""
ALPHA DOLAR 2.0 - API Module
Integração com Deriv API
"""

from .deriv_api import DerivAPI, create_deriv_client
from .trade_executor import TradeExecutor
from .data_collector import DataCollector

__all__ = [
    'DerivAPI',
    'create_deriv_client',
    'TradeExecutor',
    'DataCollector'
]