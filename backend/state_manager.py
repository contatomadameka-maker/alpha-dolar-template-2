"""
State Manager — Redis para estado compartilhado entre workers
Substitui o bots_state global em memória
"""
import os
import json
import redis
import threading

REDIS_URL = os.environ.get('REDIS_URL', '')

# Instâncias dos bots ficam em memória local (não serializáveis)
# Estado/config/trades ficam no Redis
_local_instances = {}  # {deriv_id: {bot_type: bot_instance}}
_local_lock = threading.Lock()

def _get_redis():
    """Retorna conexão Redis ou None se não disponível"""
    if not REDIS_URL:
        return None
    try:
        r = redis.from_url(REDIS_URL, decode_responses=True, socket_timeout=2)
        r.ping()
        return r
    except:
        return None

def _state_key(deriv_id, bot_type):
    return f"bot_state:{deriv_id}:{bot_type}"

def get_user_state(deriv_id, bot_type):
    """Retorna estado do bot — Redis se disponível, memória local como fallback"""
    if not deriv_id:
        deriv_id = 'anonymous'
    
    r = _get_redis()
    if r:
        try:
            key = _state_key(deriv_id, bot_type)
            data = r.get(key)
            if data:
                state = json.loads(data)
            else:
                state = _default_state()
                r.set(key, json.dumps(state), ex=86400)  # expira em 24h
            
            # Anexar instância local se existir
            with _local_lock:
                instance = _local_instances.get(deriv_id, {}).get(bot_type)
                state['_instance'] = instance
            return state
        except:
            pass
    
    # Fallback: memória local
    return _get_local_state(deriv_id, bot_type)

def update_user_state(deriv_id, bot_type, updates):
    """Atualiza estado no Redis"""
    if not deriv_id:
        deriv_id = 'anonymous'
    
    r = _get_redis()
    if r:
        try:
            key = _state_key(deriv_id, bot_type)
            data = r.get(key)
            state = json.loads(data) if data else _default_state()
            
            # Remover instância antes de serializar
            updates_clean = {k: v for k, v in updates.items() 
                           if k not in ('instance', 'thread', '_instance')}
            state.update(updates_clean)
            r.set(key, json.dumps(state), ex=86400)
            return state
        except:
            pass
    
    # Fallback: memória local
    return _update_local_state(deriv_id, bot_type, updates)

def set_bot_instance(deriv_id, bot_type, instance, thread=None):
    """Salva instância do bot em memória local (não serializável)"""
    with _local_lock:
        if deriv_id not in _local_instances:
            _local_instances[deriv_id] = {}
        _local_instances[deriv_id][bot_type] = instance

def get_bot_instance(deriv_id, bot_type):
    """Retorna instância do bot da memória local"""
    with _local_lock:
        return _local_instances.get(deriv_id, {}).get(bot_type)

def clear_bot_instance(deriv_id, bot_type):
    """Remove instância do bot"""
    with _local_lock:
        if deriv_id in _local_instances:
            _local_instances[deriv_id].pop(bot_type, None)

def _default_state():
    return {
        'running': False, 'trades': [],
        'stop_reason': None, 'stop_message': None,
        'mart_step': 0, 'mart_max': 3,
        '_perda_desde_ultimo_ganho': 0.0,
        '_lucro_desde_ultimo_reset': 0.0,
    }

# ── Fallback memória local ──
_local_states = {}

def _get_local_state(deriv_id, bot_type):
    if deriv_id not in _local_states:
        _local_states[deriv_id] = {}
    if bot_type not in _local_states[deriv_id]:
        _local_states[deriv_id][bot_type] = _default_state()
    return _local_states[deriv_id][bot_type]

def _update_local_state(deriv_id, bot_type, updates):
    state = _get_local_state(deriv_id, bot_type)
    state.update(updates)
    return state

def is_redis_available():
    return _get_redis() is not None

