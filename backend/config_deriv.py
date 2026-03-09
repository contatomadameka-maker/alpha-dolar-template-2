"""
ALPHA DOLAR 2.0 - Configuração
Configurações centralizadas do sistema
"""

# ============================================================================
# DERIV API - CONFIGURAÇÃO
# ============================================================================

DERIV_CONFIG = {
    # Conta DEMO (para testes)
    'demo': {
        'token': 'Nmw6VZ2zJp1dWY1',
        'is_demo': True,
        'endpoint': 'wss://ws.derivws.com/websockets/v3?app_id=1089'
    },

    # Conta REAL (produção)
    'real': {
        'token': None,  # Adicione seu token REAL aqui
        'is_demo': False,
        'endpoint': 'wss://ws.derivws.com/websockets/v3?app_id=1089'
    }
}

# ============================================================================
# MODOS DE OPERAÇÃO
# ============================================================================

OPERATION_MODES = {
    'simulado': {
        'name': '🎮 Simulado',
        'description': 'Ticks e trades simulados (sem API)',
        'use_real_api': False
    },
    'demo': {
        'name': '🧪 Demo (API Real)',
        'description': 'API real com conta demo ($10k virtual)',
        'use_real_api': True,
        'account_type': 'demo'
    },
    'real': {
        'name': '💰 Real (Dinheiro Real)',
        'description': 'API real com dinheiro real - CUIDADO!',
        'use_real_api': True,
        'account_type': 'real'
    }
}

# ============================================================================
# CONFIGURAÇÕES PADRÃO
# ============================================================================

DEFAULT_CONFIG = {
    'operation_mode': 'simulado',  # simulado, demo, ou real
    'auto_save_data': True,  # Salvar dados automaticamente
    'data_directory': './data',
    'enable_alerts': False,  # Alertas sonoros
    'log_level': 'INFO'
}

# ============================================================================
# MERCADOS FAVORITOS
# ============================================================================

FAVORITE_MARKETS = [
    'R_100',    # Volatility 100
    'R_50',     # Volatility 50
    'CRASH500', # Crash 500
    'BOOM500',  # Boom 500
]

# ============================================================================
# LIMITES DE SEGURANÇA
# ============================================================================

SAFETY_LIMITS = {
    'max_stake_demo': 100.0,  # Máximo por trade em demo
    'max_stake_real': 10.0,   # Máximo por trade em real
    'max_loss_per_day': 50.0, # Perda máxima por dia
    'max_trades_per_hour': 100,
    'require_confirmation_real': True  # Confirmar antes de trade real
}

# ============================================================================
# CONFIGURAÇÕES DE MACHINE LEARNING
# ============================================================================

ML_CONFIG = {
    'enabled': False,  # Habilitar ML (será True quando criar)
    'model_type': 'random_forest',  # random_forest, xgboost, lstm
    'retrain_interval': 1000,  # Retreinar a cada N trades
    'min_confidence': 0.60,  # Confiança mínima para operar
}


def get_deriv_token(account_type='demo'):
    """Retorna token de acordo com tipo de conta"""
    return DERIV_CONFIG.get(account_type, {}).get('token')


def is_real_mode(operation_mode):
    """Verifica se está em modo real"""
    return operation_mode == 'real'


def get_max_stake(operation_mode):
    """Retorna stake máximo baseado no modo"""
    if operation_mode == 'real':
        return SAFETY_LIMITS['max_stake_real']
    return SAFETY_LIMITS['max_stake_demo']


if __name__ == "__main__":
    print("=" * 60)
    print("CONFIGURAÇÃO DO ALPHA DOLAR 2.0")
    print("=" * 60)

    print(f"\n📋 Modos de operação disponíveis:")
    for key, mode in OPERATION_MODES.items():
        print(f"   {mode['name']}: {mode['description']}")

    print(f"\n🔐 Token DEMO configurado: {'✅ Sim' if DERIV_CONFIG['demo']['token'] else '❌ Não'}")
    print(f"🔐 Token REAL configurado: {'✅ Sim' if DERIV_CONFIG['real']['token'] else '❌ Não'}")

    print(f"\n🛡️ Limites de segurança:")
    print(f"   Max stake DEMO: ${SAFETY_LIMITS['max_stake_demo']}")
    print(f"   Max stake REAL: ${SAFETY_LIMITS['max_stake_real']}")
    print(f"   Max perda/dia: ${SAFETY_LIMITS['max_loss_per_day']}")

    print(f"\n✅ Configuração carregada com sucesso!")