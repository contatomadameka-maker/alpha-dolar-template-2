"""
ALPHA DOLAR 2.0 - Tipos de Contrato
Todos os tipos de negociação disponíveis na Deriv API
"""

CONTRACT_TYPES = {
    "digits": {
        "name": "Dígitos",
        "icon": "🎲",
        "types": [
            {
                "type": "DIGITOVER",
                "name": "Superior/Inferior - Over",
                "icon": "⬆️",
                "description": "Último dígito será MAIOR que",
                "requires_barrier": True,
                "barrier_range": [0, 9]
            },
            {
                "type": "DIGITUNDER",
                "name": "Superior/Inferior - Under",
                "icon": "⬇️",
                "description": "Último dígito será MENOR que",
                "requires_barrier": True,
                "barrier_range": [0, 9]
            },
            {
                "type": "DIGITMATCH",
                "name": "Combina",
                "icon": "🎯",
                "description": "Último dígito será IGUAL a",
                "requires_barrier": True,
                "barrier_range": [0, 9]
            },
            {
                "type": "DIGITDIFF",
                "name": "Difere",
                "icon": "❌",
                "description": "Último dígito será DIFERENTE de",
                "requires_barrier": True,
                "barrier_range": [0, 9]
            },
            {
                "type": "DIGITEVEN",
                "name": "Par",
                "icon": "🔵",
                "description": "Último dígito será PAR (0,2,4,6,8)",
                "requires_barrier": False
            },
            {
                "type": "DIGITODD",
                "name": "Ímpar",
                "icon": "🔴",
                "description": "Último dígito será ÍMPAR (1,3,5,7,9)",
                "requires_barrier": False
            }
        ]
    },

    "rise_fall": {
        "name": "Subindo ou Descendo",
        "icon": "📈",
        "types": [
            {
                "type": "CALL",
                "name": "Rise",
                "icon": "⬆️",
                "description": "Mercado vai SUBIR",
                "requires_barrier": False
            },
            {
                "type": "PUT",
                "name": "Fall",
                "icon": "⬇️",
                "description": "Mercado vai CAIR",
                "requires_barrier": False
            },
            {
                "type": "CALLE",
                "name": "Rise Equal",
                "icon": "⬆️=",
                "description": "Mercado vai SUBIR ou EMPATAR",
                "requires_barrier": False
            },
            {
                "type": "PUTE",
                "name": "Fall Equal",
                "icon": "⬇️=",
                "description": "Mercado vai CAIR ou EMPATAR",
                "requires_barrier": False
            }
        ]
    },

    "reset": {
        "name": "Reset",
        "icon": "🔄",
        "types": [
            {
                "type": "RESETCALL",
                "name": "Reset Call",
                "icon": "🔄⬆️",
                "description": "Reset e depois sobe",
                "requires_barrier": False
            },
            {
                "type": "RESETPUT",
                "name": "Reset Put",
                "icon": "🔄⬇️",
                "description": "Reset e depois cai",
                "requires_barrier": False
            }
        ]
    },

    "only_ups_downs": {
        "name": "Only Ups/Downs",
        "icon": "🎯",
        "types": [
            {
                "type": "UPORDOWN",
                "name": "Only Ups",
                "icon": "📈",
                "description": "Todos os ticks devem subir",
                "requires_barrier": False
            },
            {
                "type": "UPORDOWN",
                "name": "Only Downs",
                "icon": "📉",
                "description": "Todos os ticks devem cair",
                "requires_barrier": False
            }
        ]
    },

    "high_low": {
        "name": "High/Low Ticks",
        "icon": "📊",
        "types": [
            {
                "type": "TICKHIGH",
                "name": "High Tick",
                "icon": "🔝",
                "description": "Tick mais alto no período",
                "requires_barrier": False
            },
            {
                "type": "TICKLOW",
                "name": "Low Tick",
                "icon": "🔻",
                "description": "Tick mais baixo no período",
                "requires_barrier": False
            }
        ]
    },

    "touch": {
        "name": "Touch/No Touch",
        "icon": "👆",
        "types": [
            {
                "type": "ONETOUCH",
                "name": "Touch",
                "icon": "✅",
                "description": "Mercado vai TOCAR a barreira",
                "requires_barrier": True,
                "barrier_type": "price"
            },
            {
                "type": "NOTOUCH",
                "name": "No Touch",
                "icon": "🚫",
                "description": "Mercado NÃO vai tocar a barreira",
                "requires_barrier": True,
                "barrier_type": "price"
            }
        ]
    },

    "higher_lower": {
        "name": "Higher/Lower",
        "icon": "🎚️",
        "types": [
            {
                "type": "HIGHER",
                "name": "Higher",
                "icon": "⬆️",
                "description": "Termina ACIMA da barreira",
                "requires_barrier": True,
                "barrier_type": "price"
            },
            {
                "type": "LOWER",
                "name": "Lower",
                "icon": "⬇️",
                "description": "Termina ABAIXO da barreira",
                "requires_barrier": True,
                "barrier_type": "price"
            }
        ]
    },

    "in_out": {
        "name": "Stays/Goes",
        "icon": "🎯",
        "types": [
            {
                "type": "RANGE",
                "name": "Stays Between",
                "icon": "↔️",
                "description": "Fica DENTRO das barreiras",
                "requires_barrier": True,
                "barrier_type": "range"
            },
            {
                "type": "UPORDOWN",
                "name": "Goes Outside",
                "icon": "↕️",
                "description": "Sai FORA das barreiras",
                "requires_barrier": True,
                "barrier_type": "range"
            }
        ]
    },

    "ends": {
        "name": "Ends Between/Outside",
        "icon": "🏁",
        "types": [
            {
                "type": "EXPIRY",
                "name": "Ends Between",
                "icon": "🎯",
                "description": "Termina ENTRE as barreiras",
                "requires_barrier": True,
                "barrier_type": "range"
            },
            {
                "type": "EXPIRY",
                "name": "Ends Outside",
                "icon": "🚫",
                "description": "Termina FORA das barreiras",
                "requires_barrier": True,
                "barrier_type": "range"
            }
        ]
    },

    "asian": {
        "name": "Asian",
        "icon": "🌏",
        "types": [
            {
                "type": "ASIANU",
                "name": "Asian Up",
                "icon": "⬆️",
                "description": "Média sobe",
                "requires_barrier": False
            },
            {
                "type": "ASIAND",
                "name": "Asian Down",
                "icon": "⬇️",
                "description": "Média cai",
                "requires_barrier": False
            }
        ]
    }
}


def get_all_contract_types():
    """Retorna todos os tipos de contrato disponíveis"""
    all_types = []
    for category_key, category_data in CONTRACT_TYPES.items():
        for contract in category_data["types"]:
            contract["category"] = category_data["name"]
            contract["category_icon"] = category_data["icon"]
            contract["category_key"] = category_key
            all_types.append(contract)
    return all_types


def get_contracts_by_category(category_key):
    """Retorna contratos de uma categoria específica"""
    if category_key in CONTRACT_TYPES:
        return CONTRACT_TYPES[category_key]["types"]
    return []


def get_contract_info(contract_type):
    """Retorna informações de um tipo de contrato específico"""
    for category_data in CONTRACT_TYPES.values():
        for contract in category_data["types"]:
            if contract["type"] == contract_type:
                return contract
    return None


# Durações disponíveis
DURATIONS = {
    "ticks": {
        "name": "Ticks",
        "icon": "⏱️",
        "unit": "t",
        "values": [1, 2, 3, 4, 5, 10, 15, 20, 25, 50, 100]
    },
    "seconds": {
        "name": "Segundos",
        "icon": "⏱️",
        "unit": "s",
        "values": [15, 30, 45, 60, 90, 120, 180, 240, 300]
    },
    "minutes": {
        "name": "Minutos",
        "icon": "⏲️",
        "unit": "m",
        "values": [1, 2, 3, 4, 5, 10, 15, 30, 60]
    },
    "hours": {
        "name": "Horas",
        "icon": "🕐",
        "unit": "h",
        "values": [1, 2, 4, 8, 12, 24]
    },
    "days": {
        "name": "Dias",
        "icon": "📅",
        "unit": "d",
        "values": [1, 2, 3, 5, 7, 14, 30]
    }
}


# Lista de categorias para exibição
CATEGORIES = [
    {"key": "digits", "name": "Dígitos", "icon": "🎲"},
    {"key": "rise_fall", "name": "Subindo/Descendo", "icon": "📈"},
    {"key": "reset", "name": "Reset", "icon": "🔄"},
    {"key": "only_ups_downs", "name": "Only Ups/Downs", "icon": "🎯"},
    {"key": "high_low", "name": "High/Low Ticks", "icon": "📊"},
    {"key": "touch", "name": "Touch/No Touch", "icon": "👆"},
    {"key": "higher_lower", "name": "Higher/Lower", "icon": "🎚️"},
    {"key": "in_out", "name": "Stays/Goes", "icon": "🎯"},
    {"key": "ends", "name": "Ends Between/Outside", "icon": "🏁"},
    {"key": "asian", "name": "Asian", "icon": "🌏"},
]


if __name__ == "__main__":
    # Teste
    print("=" * 60)
    print("TIPOS DE CONTRATO DISPONÍVEIS NO ALPHA DOLAR 2.0")
    print("=" * 60)

    for category in CATEGORIES:
        contracts = get_contracts_by_category(category["key"])
        print(f"\n{category['icon']} {category['name']} ({len(contracts)} tipos)")
        for contract in contracts:
            barrier_info = "🎯 Barreira" if contract.get("requires_barrier") else "✅ Sem barreira"
            print(f"   {contract['icon']} {contract['name']} - {barrier_info}")

    print(f"\n✅ Total de tipos: {len(get_all_contract_types())}")