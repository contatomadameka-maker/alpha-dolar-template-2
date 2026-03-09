"""
ALPHA DOLAR 2.0 - Dados de Mercados
Todos os mercados disponíveis na Deriv API com ícones
"""

# Símbolos reais da Deriv API
MARKETS = {
    "volatility_continuous": {
        "name": "Índices Contínuos",
        "icon": "📊",
        "markets": [
            {"symbol": "R_10", "name": "Volatility 10 Index", "icon": "🔟", "tick": "1s"},
            {"symbol": "R_25", "name": "Volatility 25 Index", "icon": "2️⃣5️⃣", "tick": "1s"},
            {"symbol": "R_50", "name": "Volatility 50 Index", "icon": "5️⃣0️⃣", "tick": "1s"},
            {"symbol": "R_75", "name": "Volatility 75 Index", "icon": "7️⃣5️⃣", "tick": "1s"},
            {"symbol": "R_100", "name": "Volatility 100 Index", "icon": "💯", "tick": "1s"},
            {"symbol": "1HZ10V", "name": "Volatility 10 (1s) Index", "icon": "⚡", "tick": "0.1s"},
            {"symbol": "1HZ25V", "name": "Volatility 25 (1s) Index", "icon": "⚡", "tick": "0.1s"},
            {"symbol": "1HZ50V", "name": "Volatility 50 (1s) Index", "icon": "⚡", "tick": "0.1s"},
            {"symbol": "1HZ75V", "name": "Volatility 75 (1s) Index", "icon": "⚡", "tick": "0.1s"},
            {"symbol": "1HZ100V", "name": "Volatility 100 (1s) Index", "icon": "⚡", "tick": "0.1s"},
            {"symbol": "1HZ150V", "name": "Volatility 150 (1s) Index", "icon": "⚡", "tick": "0.1s"},
            {"symbol": "1HZ200V", "name": "Volatility 200 (1s) Index", "icon": "⚡", "tick": "0.1s"},
            {"symbol": "1HZ250V", "name": "Volatility 250 (1s) Index", "icon": "⚡", "tick": "0.1s"},
            {"symbol": "1HZ300V", "name": "Volatility 300 (1s) Index", "icon": "⚡", "tick": "0.1s"},
        ]
    },

    "volatility_jump": {
        "name": "Índices Jump",
        "icon": "🦘",
        "markets": [
            {"symbol": "JD10", "name": "Jump 10 Index", "icon": "🔟", "tick": "1s"},
            {"symbol": "JD25", "name": "Jump 25 Index", "icon": "2️⃣5️⃣", "tick": "1s"},
            {"symbol": "JD50", "name": "Jump 50 Index", "icon": "5️⃣0️⃣", "tick": "1s"},
            {"symbol": "JD75", "name": "Jump 75 Index", "icon": "7️⃣5️⃣", "tick": "1s"},
            {"symbol": "JD100", "name": "Jump 100 Index", "icon": "💯", "tick": "1s"},
        ]
    },

    "crash_boom": {
        "name": "Índices Crash/Boom",
        "icon": "💥",
        "markets": [
            {"symbol": "CRASH300N", "name": "Crash 300 Index", "icon": "📉", "tick": "1s"},
            {"symbol": "CRASH500", "name": "Crash 500 Index", "icon": "📉", "tick": "1s"},
            {"symbol": "CRASH600N", "name": "Crash 600 Index", "icon": "📉", "tick": "1s"},
            {"symbol": "CRASH900N", "name": "Crash 900 Index", "icon": "📉", "tick": "1s"},
            {"symbol": "CRASH1000", "name": "Crash 1000 Index", "icon": "📉", "tick": "1s"},
            {"symbol": "BOOM300N", "name": "Boom 300 Index", "icon": "📈", "tick": "1s"},
            {"symbol": "BOOM500", "name": "Boom 500 Index", "icon": "📈", "tick": "1s"},
            {"symbol": "BOOM600N", "name": "Boom 600 Index", "icon": "📈", "tick": "1s"},
            {"symbol": "BOOM900N", "name": "Boom 900 Index", "icon": "📈", "tick": "1s"},
            {"symbol": "BOOM1000", "name": "Boom 1000 Index", "icon": "📈", "tick": "1s"},
        ]
    },

    "step_indices": {
        "name": "Índices Step",
        "icon": "📶",
        "markets": [
            {"symbol": "stpRNG", "name": "Step Index", "icon": "🎯", "tick": "1s"},
        ]
    },

    "range_break": {
        "name": "Range Break Indices",
        "icon": "🎲",
        "markets": [
            {"symbol": "RDBULL", "name": "Range Break 100 Index", "icon": "🐂", "tick": "1s"},
            {"symbol": "RDBEAR", "name": "Range Break 200 Index", "icon": "🐻", "tick": "1s"},
        ]
    },

    "crypto": {
        "name": "Criptomoedas",
        "icon": "₿",
        "markets": [
            {"symbol": "cryBTCUSD", "name": "BTC/USD", "icon": "₿", "tick": "real"},
            {"symbol": "cryETHUSD", "name": "ETH/USD", "icon": "Ξ", "tick": "real"},
            {"symbol": "cryLTCUSD", "name": "LTC/USD", "icon": "Ł", "tick": "real"},
        ]
    },

    "forex_major": {
        "name": "Forex - Pares Principais",
        "icon": "💱",
        "markets": [
            {"symbol": "frxEURUSD", "name": "EUR/USD", "icon": "🇪🇺🇺🇸", "tick": "real"},
            {"symbol": "frxGBPUSD", "name": "GBP/USD", "icon": "🇬🇧🇺🇸", "tick": "real"},
            {"symbol": "frxUSDJPY", "name": "USD/JPY", "icon": "🇺🇸🇯🇵", "tick": "real"},
            {"symbol": "frxAUDUSD", "name": "AUD/USD", "icon": "🇦🇺🇺🇸", "tick": "real"},
            {"symbol": "frxUSDCAD", "name": "USD/CAD", "icon": "🇺🇸🇨🇦", "tick": "real"},
            {"symbol": "frxUSDCHF", "name": "USD/CHF", "icon": "🇺🇸🇨🇭", "tick": "real"},
            {"symbol": "frxNZDUSD", "name": "NZD/USD", "icon": "🇳🇿🇺🇸", "tick": "real"},
        ]
    },

    "forex_minor": {
        "name": "Forex - Pares Secundários",
        "icon": "💱",
        "markets": [
            {"symbol": "frxEURGBP", "name": "EUR/GBP", "icon": "🇪🇺🇬🇧", "tick": "real"},
            {"symbol": "frxEURJPY", "name": "EUR/JPY", "icon": "🇪🇺🇯🇵", "tick": "real"},
            {"symbol": "frxGBPJPY", "name": "GBP/JPY", "icon": "🇬🇧🇯🇵", "tick": "real"},
            {"symbol": "frxAUDCAD", "name": "AUD/CAD", "icon": "🇦🇺🇨🇦", "tick": "real"},
            {"symbol": "frxAUDCHF", "name": "AUD/CHF", "icon": "🇦🇺🇨🇭", "tick": "real"},
            {"symbol": "frxAUDJPY", "name": "AUD/JPY", "icon": "🇦🇺🇯🇵", "tick": "real"},
            {"symbol": "frxAUDNZD", "name": "AUD/NZD", "icon": "🇦🇺🇳🇿", "tick": "real"},
            {"symbol": "frxEURAUD", "name": "EUR/AUD", "icon": "🇪🇺🇦🇺", "tick": "real"},
            {"symbol": "frxEURCAD", "name": "EUR/CAD", "icon": "🇪🇺🇨🇦", "tick": "real"},
            {"symbol": "frxEURCHF", "name": "EUR/CHF", "icon": "🇪🇺🇨🇭", "tick": "real"},
            {"symbol": "frxEURNZD", "name": "EUR/NZD", "icon": "🇪🇺🇳🇿", "tick": "real"},
            {"symbol": "frxGBPAUD", "name": "GBP/AUD", "icon": "🇬🇧🇦🇺", "tick": "real"},
            {"symbol": "frxGBPCAD", "name": "GBP/CAD", "icon": "🇬🇧🇨🇦", "tick": "real"},
            {"symbol": "frxGBPCHF", "name": "GBP/CHF", "icon": "🇬🇧🇨🇭", "tick": "real"},
            {"symbol": "frxGBPNZD", "name": "GBP/NZD", "icon": "🇬🇧🇳🇿", "tick": "real"},
        ]
    },

    "commodities": {
        "name": "Metais",
        "icon": "🥇",
        "markets": [
            {"symbol": "frxXAUUSD", "name": "Gold/USD", "icon": "🥇", "tick": "real"},
            {"symbol": "frxXAGUSD", "name": "Silver/USD", "icon": "🥈", "tick": "real"},
            {"symbol": "frxXPDUSD", "name": "Palladium/USD", "icon": "⚪", "tick": "real"},
            {"symbol": "frxXPTUSD", "name": "Platinum/USD", "icon": "⚫", "tick": "real"},
        ]
    },

    "stock_indices": {
        "name": "Índices de Ações",
        "icon": "📊",
        "markets": [
            {"symbol": "OTC_AEX", "name": "Netherlands 25", "icon": "🇳🇱", "tick": "real"},
            {"symbol": "OTC_AS51", "name": "Australia 200", "icon": "🇦🇺", "tick": "real"},
            {"symbol": "OTC_DJI", "name": "Wall Street 30", "icon": "🇺🇸", "tick": "real"},
            {"symbol": "OTC_FCHI", "name": "France 40", "icon": "🇫🇷", "tick": "real"},
            {"symbol": "OTC_FTSE", "name": "UK 100", "icon": "🇬🇧", "tick": "real"},
            {"symbol": "OTC_GDAXI", "name": "Germany 40", "icon": "🇩🇪", "tick": "real"},
            {"symbol": "OTC_HSI", "name": "Hong Kong 50", "icon": "🇭🇰", "tick": "real"},
            {"symbol": "OTC_N225", "name": "Japan 225", "icon": "🇯🇵", "tick": "real"},
            {"symbol": "OTC_SPC", "name": "US 500", "icon": "🇺🇸", "tick": "real"},
            {"symbol": "OTC_SSMI", "name": "Swiss 20", "icon": "🇨🇭", "tick": "real"},
            {"symbol": "OTC_SX5E", "name": "Euro 50", "icon": "🇪🇺", "tick": "real"},
        ]
    }
}


def get_all_markets():
    """Retorna todos os mercados disponíveis"""
    all_markets = []
    for category_key, category_data in MARKETS.items():
        for market in category_data["markets"]:
            market["category"] = category_data["name"]
            market["category_icon"] = category_data["icon"]
            all_markets.append(market)
    return all_markets


def get_markets_by_category(category_key):
    """Retorna mercados de uma categoria específica"""
    if category_key in MARKETS:
        return MARKETS[category_key]["markets"]
    return []


def get_market_info(symbol):
    """Retorna informações de um mercado específico"""
    for category_data in MARKETS.values():
        for market in category_data["markets"]:
            if market["symbol"] == symbol:
                return market
    return None


def search_markets(query):
    """Busca mercados por nome ou símbolo"""
    query = query.lower()
    results = []
    for market in get_all_markets():
        if query in market["name"].lower() or query in market["symbol"].lower():
            results.append(market)
    return results


# Lista de categorias para exibição
CATEGORIES = [
    {"key": "volatility_continuous", "name": "Índices Contínuos", "icon": "📊"},
    {"key": "volatility_jump", "name": "Índices Jump", "icon": "🦘"},
    {"key": "crash_boom", "name": "Crash/Boom", "icon": "💥"},
    {"key": "step_indices", "name": "Step Indices", "icon": "📶"},
    {"key": "range_break", "name": "Range Break", "icon": "🎲"},
    {"key": "crypto", "name": "Criptomoedas", "icon": "₿"},
    {"key": "forex_major", "name": "Forex Principal", "icon": "💱"},
    {"key": "forex_minor", "name": "Forex Secundário", "icon": "💱"},
    {"key": "commodities", "name": "Metais", "icon": "🥇"},
    {"key": "stock_indices", "name": "Índices de Ações", "icon": "📊"},
]


if __name__ == "__main__":
    # Teste
    print("=" * 60)
    print("MERCADOS DISPONÍVEIS NO ALPHA DOLAR 2.0")
    print("=" * 60)

    for category in CATEGORIES:
        markets = get_markets_by_category(category["key"])
        print(f"\n{category['icon']} {category['name']} ({len(markets)} mercados)")
        for market in markets[:3]:  # Mostra apenas 3 primeiros
            print(f"   {market['icon']} {market['name']} ({market['symbol']})")
        if len(markets) > 3:
            print(f"   ... e mais {len(markets) - 3} mercados")

    print(f"\n✅ Total de mercados: {len(get_all_markets())}")