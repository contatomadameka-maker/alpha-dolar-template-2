"""
ALPHA DOLAR 2.0 - Markets Module
Módulo de mercados e tipos de contrato
"""

from .markets_data import (
    MARKETS,
    CATEGORIES as MARKET_CATEGORIES,
    get_all_markets,
    get_markets_by_category,
    get_market_info,
    search_markets
)

from .contract_types import (
    CONTRACT_TYPES,
    CATEGORIES as CONTRACT_CATEGORIES,
    DURATIONS,
    get_all_contract_types,
    get_contracts_by_category,
    get_contract_info
)

__all__ = [
    'MARKETS',
    'MARKET_CATEGORIES',
    'CONTRACT_TYPES',
    'CONTRACT_CATEGORIES',
    'DURATIONS',
    'get_all_markets',
    'get_markets_by_category',
    'get_market_info',
    'search_markets',
    'get_all_contract_types',
    'get_contracts_by_category',
    'get_contract_info'
]
