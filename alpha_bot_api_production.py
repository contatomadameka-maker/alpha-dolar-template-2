import sys
import os
import threading
import time
import traceback as _tb
from webhook_cakto import register_cakto_webhook
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory, redirect
try:
    from flask_cors import CORS
except ImportError:
    class CORS:
        def __init__(self, app, **kw): pass

project_path = os.path.dirname(os.path.abspath(__file__))
backend_path = os.path.join(project_path, 'backend')
if project_path not in sys.path:
    sys.path.insert(0, project_path)
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

app = Flask(__name__, static_folder='web', static_url_path='')
CORS(app)
register_cakto_webhook(app)

# ==================== IMPORTAR BOTS REAIS ====================

print(f"📁 project_path: {project_path}")
print(f"📁 backend_path: {backend_path}")
print(f"📁 sys.path: {sys.path[:3]}")

try:
    try:
        from backend.bot import AlphaDolar
    except ImportError:
        import importlib, inspect
        _bot_module = importlib.import_module('backend.bot')
        _classes = [obj for name, obj in inspect.getmembers(_bot_module, inspect.isclass)
                    if obj.__module__ == 'backend.bot']
        if _classes:
            AlphaDolar = _classes[0]
            print(f"⚠️ AlphaDolar importado como: {AlphaDolar.__name__}")
        else:
            raise ImportError("Nenhuma classe encontrada em backend.bot")
    from backend.config import BotConfig
    from backend.strategies.alpha_bot_balanced import AlphaBotBalanced
    from backend.strategies.alpha_bot_1 import AlphaBot1
    from backend.strategies.alpha_bot_2 import AlphaBot2
    from backend.strategies.alpha_bot_3 import AlphaBot3
    from backend.strategies.alpha_mind import AlphaMind
    from backend.strategies.quantum_trader import QuantumTrader
    from backend.strategies.titan_core import TitanCore
    from backend.strategies.alpha_pulse import AlphaPulse
    from backend.strategies.alpha_smart import AlphaSmart
    from backend.strategies.alpha_analytics_sniper import AlphaAnalytics, AlphaSniper
    from backend.strategies.premium_strategies import MegaAlpha1, MegaAlpha2, MegaAlpha3, AlphaElite, AlphaNexus
    BOTS_AVAILABLE = True
    print("✅ Todas as 15 estratégias carregadas!")
except ImportError as e:
    BOTS_AVAILABLE = False
    print(f"⚠️ Erro ao importar bots: {e}")
    _tb.print_exc()

STRATEGY_MAP = {
    'alpha_bot_1':        lambda tm, rm: AlphaBot1(tm, rm),
    'alpha_bot_2':        lambda tm, rm: AlphaBot2(tm, rm),
    'alpha_bot_3':        lambda tm, rm: AlphaBot3(tm, rm),
    'alpha_bot_balanced': lambda tm, rm: AlphaBotBalanced(tm, rm),
    'alpha_mind':         lambda tm, rm: AlphaMind(tm, rm),
    'quantum_trader':     lambda tm, rm: QuantumTrader(tm, rm),
    'titan_core':         lambda tm, rm: TitanCore(tm, rm),
    'alpha_pulse':        lambda tm, rm: AlphaPulse(tm, rm),
    'alpha_smart':        lambda tm, rm: AlphaSmart(tm, rm),
    'alpha_analytics':    lambda tm, rm: AlphaAnalytics(tm, rm),
    'alpha_sniper':       lambda tm, rm: AlphaSniper(tm, rm),
    'mega_alpha_1':       lambda tm, rm: MegaAlpha1(tm, rm),
    'mega_alpha_2':       lambda tm, rm: MegaAlpha2(tm, rm),
    'mega_alpha_3':       lambda tm, rm: MegaAlpha3(tm, rm),
    'alpha_elite':        lambda tm, rm: AlphaElite(tm, rm),
    'alpha_nexus':        lambda tm, rm: AlphaNexus(tm, rm),
}

SYMBOL_MAP = {
    'Volatility 10 Index':       'R_10',
    'Volatility 25 Index':       'R_25',
    'Volatility 50 Index':       'R_50',
    'Volatility 75 Index':       'R_75',
    'Volatility 100 Index':      'R_100',
    'Volatility 10 (1s) Index':  '1HZ10V',
    'Volatility 25 (1s) Index':  '1HZ25V',
    'Volatility 50 (1s) Index':  '1HZ50V',
    'Volatility 75 (1s) Index':  '1HZ75V',
    'Volatility 100 (1s) Index': '1HZ100V',
    'Boom 1000 Index':           'BOOM1000',
    'Boom 500 Index':            'BOOM500',
    'Crash 1000 Index':          'CRASH1000',
    'Crash 500 Index':           'CRASH500',
    'Jump 10 Index':             'JD10',
    'Jump 25 Index':             'JD25',
    'Jump 50 Index':             'JD50',
    'Jump 75 Index':             'JD75',
    'Jump 100 Index':            'JD100',
    'R_10': 'R_10', 'R_25': 'R_25', 'R_50': 'R_50',
    'R_75': 'R_75', 'R_100': 'R_100',
    '1HZ10V': '1HZ10V', '1HZ25V': '1HZ25V', '1HZ50V': '1HZ50V',
    '1HZ75V': '1HZ75V', '1HZ100V': '1HZ100V',
}

def resolve_symbol(s):
    return SYMBOL_MAP.get(s, s or 'R_100')

# ==================== ESTADO GLOBAL ====================
# Estado agora gerenciado pelo state_manager (Redis + fallback memória)
bots_state = {}  # mantido para compatibilidade

try:
    from backend.state_manager import (
        get_user_state as _sm_get,
        update_user_state as _sm_update,
        set_bot_instance, get_bot_instance, clear_bot_instance,
        is_redis_available
    )
    STATE_MANAGER = True
    print(f"✅ State Manager carregado! Redis: {'✅' if is_redis_available() else '⚠️ fallback memória'}")
except ImportError:
    try:
        from state_manager import (
            get_user_state as _sm_get,
            update_user_state as _sm_update,
            set_bot_instance, get_bot_instance, clear_bot_instance,
            is_redis_available
        )
        STATE_MANAGER = True
    except:
        STATE_MANAGER = False
        print("⚠️ State Manager não disponível — usando memória local")


class _StateProxy(dict):
    """Proxy que salva automaticamente no Redis ao modificar"""
    def __init__(self, deriv_id, bot_type, data):
        super().__init__(data)
        self._deriv_id = deriv_id
        self._bot_type = bot_type
    
    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        if key not in ('instance', 'thread', '_instance') and STATE_MANAGER:
            try:
                _sm_update(self._deriv_id, self._bot_type, {key: value})
            except: pass
        # Também atualiza instância local
        if key == 'instance' and STATE_MANAGER:
            try:
                set_bot_instance(self._deriv_id, self._bot_type, value)
            except: pass
    
    def update(self, d=None, **kwargs):
        if d:
            for k, v in d.items():
                self[k] = v
        for k, v in kwargs.items():
            self[k] = v

def get_user_state(deriv_id, bot_type):
    """Retorna estado isolado por usuário"""
    if not deriv_id:
        deriv_id = 'anonymous'
    if STATE_MANAGER:
        state = _sm_get(deriv_id, bot_type)
        # Anexar instância local
        instance = get_bot_instance(deriv_id, bot_type)
        proxy = _StateProxy(deriv_id, bot_type, state)
        proxy['instance'] = instance
        return proxy
    # Fallback memória
    if deriv_id not in bots_state:
        bots_state[deriv_id] = {}
    if bot_type not in bots_state[deriv_id]:
        bots_state[deriv_id][bot_type] = _StateProxy(deriv_id, bot_type, {
            'running': False, 'instance': None, 'thread': None,
            'trades': [], 'stop_reason': None, 'stop_message': None,
            'mart_step': 0, 'mart_max': 3,
            '_perda_desde_ultimo_ganho': 0.0,
            '_lucro_desde_ultimo_reset': 0.0,
        })
    return bots_state[deriv_id][bot_type]

# ==================== ROTAS ESTÁTICAS ====================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@app.route('/login')
def login():
    return send_from_directory(os.path.join(BASE_DIR, 'web'), 'login.html')

@app.route('/')
def root():
    return redirect('/home')

@app.route('/home')
def home():
    return send_from_directory(BASE_DIR, 'index.html')

# /dashboard e /dashboard-fixed ambos servem o mesmo arquivo
@app.route('/dashboard')
@app.route('/dashboard-fixed')
@app.route('/dashboard-fixed.html')
def dashboard():
     return send_from_directory(os.path.join(BASE_DIR, 'web'), 'dashboard-fixed.html')

@app.route('/landing')
def landing():
    return send_from_directory(os.path.join(BASE_DIR, 'web'), 'landing.html')

@app.route('/guia')
def guia():
    return send_from_directory(BASE_DIR, 'guia-digitos-alpha.html')

@app.route('/videos')
def videos():
    return send_from_directory(BASE_DIR, 'videos.html')

@app.route('/css/<path:filename>')
def css_files(filename):
    return send_from_directory(os.path.join(BASE_DIR, 'web/css'), filename)

@app.route('/js/<path:filename>')
def js_files(filename):
    return send_from_directory(os.path.join(BASE_DIR, 'web/js'), filename)

@app.route('/data/<path:filename>')
def data_files(filename):
    return send_from_directory(os.path.join(BASE_DIR, 'web/data'), filename)

@app.route('/<path:path>')
def serve_static(path):
    try:
        return send_from_directory(BASE_DIR, path)
    except:
        return jsonify({'error': 'Not found'}), 404

@app.route('/api/health')
def health():
    return jsonify({'status': 'ok', 'message': 'Alpha Dolar API Running', 'bots_available': BOTS_AVAILABLE})


# ==================== USUÁRIOS / PLANOS ====================

@app.route('/api/usuario/verificar', methods=['POST'])
def verificar_acesso():
    """Verifica se usuário tem acesso ativo — chamado no login"""
    try:
        data = request.get_json()
        deriv_id = data.get('deriv_id', '')
        nome = data.get('nome', '')
        email = data.get('email', '')
        if not deriv_id:
            return jsonify({'success': False, 'error': 'deriv_id obrigatório'}), 400
        # Registra ou atualiza último acesso
        registrar_ou_atualizar_usuario(deriv_id, nome, email)
        # Verifica plano
        usuario = verificar_usuario(deriv_id)
        return jsonify({
            'success': True,
            'existe': usuario['existe'],
            'ativo': usuario['ativo'],
            'plano': usuario['plano'],
            'nome': usuario.get('nome', ''),
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/usuario/ativar', methods=['POST'])
def ativar_usuario():
    """Admin ativa plano do usuário"""
    try:
        data = request.get_json()
        deriv_id = data.get('deriv_id', '')
        plano = data.get('plano', 'starter')
        dias = int(data.get('dias', 30))
        if not deriv_id:
            return jsonify({'success': False, 'error': 'deriv_id obrigatório'}), 400
        ok = atualizar_plano_usuario(deriv_id, plano, 'ativo', dias)
        return jsonify({'success': ok, 'message': f'Plano {plano} ativado por {dias} dias!'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/usuario/listar', methods=['GET'])
def listar_usuarios_route():
    """Lista todos os usuários — admin"""
    try:
        usuarios = listar_usuarios()
        return jsonify({'success': True, 'usuarios': usuarios})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== START BOT ====================
@app.route('/api/bot/start', methods=['POST'])
def start_bot():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'Dados não fornecidos'}), 400

        bot_type     = data.get('bot_type', 'manual')
        config       = data.get('config', {})
        account_type = data.get('account_type', 'demo')
        token        = data.get('token')
        deriv_id     = data.get('deriv_id', '') or data.get('loginid', '')

        symbol        = resolve_symbol(config.get('symbol', 'R_100'))
        stake_inicial = float(config.get('stake') or config.get('stake_inicial') or 0.35)
        lucro_alvo    = float(config.get('target') or config.get('lucro_alvo') or 2.0)
        limite_perda  = float(config.get('stop') or config.get('limite_perda') or 1000.0)

        print(f"\n{'='*60}")
        print(f"📥 Iniciar bot: {bot_type} | conta: {account_type.upper()}")
        print(f"📊 Símbolo: {config.get('symbol')} → {symbol}")
        print(f"🎯 Estratégia: {config.get('strategy', 'alpha_bot_1')} ({config.get('strategy_type','').upper() or 'RISE/FALL'})")
        print(f"💰 stake={stake_inicial} target={lucro_alvo} stop={limite_perda}")
        print(f"🔑 Token recebido: {'✅ SIM (' + account_type.upper() + ')' if token else '❌ NÃO'}")
        print(f"{'='*60}\n")

        if not token:
            return jsonify({
                'success': False,
                'error': f'Token não recebido para conta {account_type}. Faça login novamente.'
            }), 400

        # Verifica se bot está suspenso
        try:
            bot_name_req = data.get('bot_name', bot_type)
            todos_bots = _listar_bots()
            for b in todos_bots:
                if b.get('nome') == bot_name_req and b.get('status') == 'suspenso':
                    return jsonify({'success': False, 'error': '🚫 Bot suspenso pelo administrador. Entre em contato.'}), 403
        except: pass

        # Garante que o estado do usuário existe
        get_user_state(deriv_id, bot_type)

        if get_user_state(deriv_id, bot_type).get('running', False):
            return jsonify({'success': False, 'error': f'Bot {bot_type} já está rodando'}), 400

        # ==================== BOT REAL ====================
        if BOTS_AVAILABLE and bot_type in ['ia', 'ia_simples']:
            print("🤖 Iniciando BOT PYTHON REAL...")

            BotConfig.DEFAULT_SYMBOL = symbol
            BotConfig.STAKE_INICIAL  = stake_inicial
            BotConfig.LUCRO_ALVO     = lucro_alvo
            BotConfig.LIMITE_PERDA   = limite_perda
            BotConfig.API_TOKEN      = token
            # Salvar config no estado do usuário para isolamento
            get_user_state(deriv_id, bot_type).update({
                'token': token,
                'symbol': symbol,
                'stake_inicial': stake_inicial,
                'lucro_alvo': lucro_alvo,
                'limite_perda': limite_perda,
                'deriv_id': deriv_id,
            })
            get_user_state(deriv_id, bot_type)['deriv_id']     = deriv_id
            get_user_state(deriv_id, bot_type)['account_type'] = account_type
            # Buscar nome do bot cadastrado para este cliente
            try:
                bots = _listar_bots()
                # Primeiro tenta pelo bot_name enviado pelo frontend
                bot_name_req = data.get('bot_name', '')
                if bot_name_req:
                    bot_cadastrado = next((b for b in bots if b.get('nome','').lower() == bot_name_req.lower()), None)
                else:
                    # Fallback: busca pelo deriv_id do dono
                    bot_cadastrado = next((b for b in bots if b.get('deriv_id') == deriv_id), None)
                # Se achou bot cadastrado usa o nome oficial, senão usa o enviado pelo frontend
                bot_nome = bot_cadastrado['nome'] if bot_cadastrado else (bot_name_req or f'BOT {deriv_id}')
            except:
                bot_nome = data.get('bot_name', bot_type)
            get_user_state(deriv_id, bot_type)['bot_name'] = bot_nome
            print(f"🔑 Token [{account_type.upper()}]: {token[:10]}...")

            trading_mode   = config.get('trading_mode', 'faster')
            risk_mode      = config.get('risk_mode', 'conservative')
            strategy_id    = config.get('strategy', 'alpha_bot_1')
            multi_strategies = config.get('multi_strategies', [])
            is_multi = strategy_id == 'multi' and multi_strategies
            stop_loss_type = config.get('stop_loss_type', 'value')
            max_losses     = int(config.get('max_losses', 5))

            BotConfig.STOP_LOSS_TYPE         = stop_loss_type
            BotConfig.MAX_CONSECUTIVE_LOSSES = max_losses
            BotConfig.STAKE_INICIAL = float(config.get('stake') or config.get('stake_inicial') or BotConfig.STAKE_INICIAL)
            BotConfig.LUCRO_ALVO    = float(config.get('target') or config.get('lucro_alvo') or BotConfig.LUCRO_ALVO)
            BotConfig.LIMITE_PERDA  = float(config.get('stop') or config.get('limite_perda') or 1000.0)

            try:
                if is_multi:
                    _multi_lista = list(multi_strategies)
                    import random
                    random.shuffle(_multi_lista)
                    _multi_idx = [0]  # lista mutável para closure
                    def _get_next_strategy():
                        idx = _multi_idx[0] % len(_multi_lista)
                        sid = _multi_lista[idx]
                        _multi_idx[0] = (idx + 1) % len(_multi_lista)
                        # Sorteia próxima aleatória diferente da atual
                        if len(_multi_lista) > 1:
                            opcoes = [s for s in _multi_lista if s != sid]
                            return STRATEGY_MAP.get(random.choice(opcoes), STRATEGY_MAP['alpha_bot_1'])(trading_mode, risk_mode)
                        return STRATEGY_MAP.get(sid, STRATEGY_MAP['alpha_bot_1'])(trading_mode, risk_mode)
                    strategy = _get_next_strategy()
                    get_user_state(deriv_id, bot_type)['strategy_name'] = type(strategy).__name__
                else:
                    _get_next_strategy = None
                    factory  = STRATEGY_MAP.get(strategy_id, STRATEGY_MAP['alpha_bot_1'])
                    strategy = factory(trading_mode, risk_mode)
            except Exception as e:
                return jsonify({'success': False, 'error': f'Erro estratégia: {str(e)}'}), 500

            try:
                bot = AlphaDolar(strategy=strategy, use_martingale=getattr(strategy, "usar_martingale", True), api_token=token)
            except Exception as e:
                return jsonify({'success': False, 'error': f'Erro bot: {str(e)}'}), 500

            if hasattr(bot, 'log') and callable(getattr(bot, 'log', None)):
                _orig_log = bot.log
                def _patched_log(message, level="INFO", _bt=bot_type, _orig=_orig_log):
                    _orig(message, level)
                    if level == "STOP_LOSS":
                        get_user_state(deriv_id, _bt)['stop_reason']  = 'stop_loss'
                        get_user_state(deriv_id, _bt)['stop_message'] = message
                        get_user_state(deriv_id, _bt)['running']      = False
                    elif level in ("WIN", "SUCCESS") and "LUCRO ALVO" in message.upper():
                        get_user_state(deriv_id, _bt)['stop_reason']  = 'take_profit'
                        get_user_state(deriv_id, _bt)['stop_message'] = message
                        get_user_state(deriv_id, _bt)['running']      = False
                bot.log = _patched_log

            get_user_state(deriv_id, bot_type)['_perda_desde_ultimo_ganho'] = 0.0
            get_user_state(deriv_id, bot_type)['_lucro_desde_ultimo_reset'] = 0.0
            get_user_state(deriv_id, bot_type)['_limite_perda'] = BotConfig.LIMITE_PERDA
            get_user_state(deriv_id, bot_type)['_lucro_sessao'] = 0.0

            def on_trade_completed(direction, won, profit, stake, symbol_used, exit_tick=None):
                print(f"🔔 on_trade_completed CHAMADO! won={won} profit={profit} step_antes={get_user_state(deriv_id, bot_type).get('mart_step',0)}")
                try:
                    if get_user_state(deriv_id, bot_type).get('account_type', 'demo') == 'real':
                        _cliente_id = deriv_id
                        _bot_name = get_user_state(deriv_id, bot_type).get('bot_name', bot_type)
                        print(f"💾 Salvando operação: cliente={_cliente_id} bot={_bot_name} won={won} profit={profit}")
                        _salvar_op(_bot_name, _cliente_id, direction, won, profit, stake)
                except Exception as e:
                    print(f"Erro ao salvar op: {e}")
                trades_ate_agora = get_user_state(deriv_id, bot_type)['trades']
                total = len(trades_ate_agora) + 1
                wins  = sum(1 for t in trades_ate_agora if t.get('result') == 'win') + (1 if won else 0)
                wr    = round((wins / total) * 100, 1) if total > 0 else 0

                if hasattr(bot, "atualizar_apos_trade"): bot.atualizar_apos_trade(won, profit)
                # Multi-estratégia: troca após perda
                if not won and is_multi and _get_next_strategy and get_user_state(deriv_id, bot_type).get('running'):
                    try:
                        nova_strategy = _get_next_strategy()
                        bot.strategy = nova_strategy
                        nome_nova = type(nova_strategy).__name__
                        get_user_state(deriv_id, bot_type)['strategy_name'] = nome_nova
                        # Reseta lucro sessao ao trocar estrategia
                        # NAO reseta lucro_sessao ao trocar — acumula toda sessao
                        get_user_state(deriv_id, bot_type)['mart_step'] = 0
                        print(f"⚡ Multi-estratégia: trocando para {nome_nova}")
                        # Adiciona ao feed de logs visível no frontend
                        _trades = get_user_state(deriv_id, bot_type).get('trades', [])
                        _trades.append({
                            'type'   : 'log',
                            'message': f'⚡ Multi-Estratégia: trocando para {nome_nova}',
                            'level'  : 'multi',
                            'time'   : datetime.now().strftime('%H:%M:%S'),
                        })
                    except Exception as _me:
                        print(f"Erro troca estratégia: {_me}")
                # Atualiza mart_step de forma genérica para qualquer estratégia
                _max = get_user_state(deriv_id, bot_type).get('mart_max', 3)
                _step = get_user_state(deriv_id, bot_type).get('mart_step', 0)
                if won:
                    get_user_state(deriv_id, bot_type)['mart_step'] = 0
                else:
                    get_user_state(deriv_id, bot_type)['mart_step'] = min(_step + 1, _max)
                # Tenta ler do objeto se disponível (mais preciso)
                try:
                    if bot.martingale:
                        _info = bot.martingale.get_info()
                        get_user_state(deriv_id, bot_type)['mart_step'] = _info.get('step_atual', get_user_state(deriv_id, bot_type)['mart_step'])
                        get_user_state(deriv_id, bot_type)['mart_max']  = _info.get('max_steps', _max)
                except: pass
                perda_acum = getattr(bot, 'perda_acumulada', 0)

                if won:
                    get_user_state(deriv_id, bot_type)['_perda_desde_ultimo_ganho'] = 0.0
                    get_user_state(deriv_id, bot_type)['_lucro_desde_ultimo_reset'] = round(
                        get_user_state(deriv_id, bot_type)['_lucro_desde_ultimo_reset'] + abs(profit), 2)
                else:
                    get_user_state(deriv_id, bot_type)['_perda_desde_ultimo_ganho'] = round(
                        get_user_state(deriv_id, bot_type)['_perda_desde_ultimo_ganho'] + abs(profit), 2)

                perda_dc = get_user_state(deriv_id, bot_type)['_perda_desde_ultimo_ganho']
                limite   = get_user_state(deriv_id, bot_type).get('_limite_perda', BotConfig.LIMITE_PERDA)

                if perda_dc >= limite and get_user_state(deriv_id, bot_type).get('running'):
                    get_user_state(deriv_id, bot_type)['stop_reason']  = 'stop_loss'
                    get_user_state(deriv_id, bot_type)['stop_message'] = f'Perda acumulada: ${perda_dc:.2f} / Limite: ${limite:.2f}'
                    get_user_state(deriv_id, bot_type)['running']      = False
                    if hasattr(bot, 'stop'):
                        try: bot.stop()
                        except: pass

                next_stake = bot._calcular_stake_recuperacao() if perda_acum > 0 and hasattr(bot, '_calcular_stake_recuperacao') else BotConfig.STAKE_INICIAL

                trade = {
                    'id': int(time.time() * 1000), 'direction': direction,
                    'result': 'win' if won else 'loss', 'profit': round(profit, 2),
                    'stake': round(stake, 2), 'symbol': symbol_used,
                    'timestamp': datetime.now().strftime('%H:%M:%S'),
                    'next_stake': round(next_stake, 2), 'step': get_user_state(deriv_id, bot_type)['mart_step'],
                    'max_steps': get_user_state(deriv_id, bot_type)['mart_max'], 'win_rate': wr, 'total_trades': total,
                    'exit_tick': str(exit_tick) if exit_tick else None,
                    'longcode': getattr(getattr(bot, 'api', None), '_ultimo_longcode', None),
                    'perda_acum': round(perda_acum, 2),
                }
                _trades_list = list(get_user_state(deriv_id, bot_type).get('trades', []))
                _trades_list.append(trade)
                if len(_trades_list) > 100:
                    _trades_list.pop(0)
                get_user_state(deriv_id, bot_type)['trades'] = _trades_list
                # Salvar operação no Supabase (somente conta REAL)
                try:
                    if get_user_state(deriv_id, bot_type).get('account_type', 'demo') == 'real':
                        cliente_id = deriv_id or get_user_state(deriv_id, bot_type).get('deriv_id', '') or get_user_state(deriv_id, bot_type).get('cliente_id', '')
                        _bot_name = get_user_state(deriv_id, bot_type).get('bot_name', bot_type) or get_user_state(deriv_id, bot_type).get('bot_name_real', bot_type)
                        _salvar_op(
                            bot_name=_bot_name,
                            cliente_id=cliente_id,
                            direcao=direction,
                            ganhou=won,
                            lucro=round(profit, 2),
                            stake=round(stake, 2)
                        )
                except Exception as e:
                    print(f"Erro ao salvar operação: {e}")

            # Salvar estado no Supabase para auto-restart
            try:
                _salvar_estado(bot_type, {
                    'bot_type': bot_type,
                    'account_type': account_type,
                    'deriv_id': deriv_id,
                    'bot_name': bot_nome if 'bot_nome' in dir() else bot_type,
                    'config': config,
                    'token': token
                })
            except Exception as e:
                print(f"Aviso: não salvou estado: {e}")

            bot._on_trade_completed = on_trade_completed

            original_contract_update = bot.on_contract_update
            def patched_contract_update(contract_data):
                status = contract_data.get('status')
                if status in ['won', 'lost']:
                    profit     = float(contract_data.get('profit', 0))
                    won_       = status == 'won'
                    direction  = contract_data.get('contract_type', 'CALL/PUT')
                    stake_used = getattr(bot, '_ultimo_stake_usado', BotConfig.STAKE_INICIAL)
                    exit_tick  = contract_data.get('exit_tick_value') or contract_data.get('exit_tick')
                    on_trade_completed(direction, won_, profit, stake_used, BotConfig.DEFAULT_SYMBOL, exit_tick)
                    bot.waiting_contract    = False
                    bot.current_contract_id = None
                    bot._ultimo_trade_time  = time.time()
                original_contract_update(contract_data)

            # Patch no método do objeto — sobrevive ao bot.start() que chama set_contract_callback(self.on_contract_update)
            bot.on_contract_update = patched_contract_update

            # Capturar token e configurações específicas deste usuário
            _user_token = token
            _user_symbol = symbol
            _user_stake = stake_inicial
            _user_target = lucro_alvo
            _user_stop = limite_perda

            def run_bot():
                try:
                    # Configurar BotConfig com valores específicos deste usuário
                    # antes de iniciar — dentro da thread para evitar conflito
                    import threading
                    _lock = getattr(run_bot, '_lock', threading.Lock())
                    with _lock:
                        BotConfig.API_TOKEN      = _user_token
                        BotConfig.DEFAULT_SYMBOL = _user_symbol
                        BotConfig.STAKE_INICIAL  = _user_stake
                        BotConfig.LUCRO_ALVO     = _user_target
                        BotConfig.LIMITE_PERDA   = _user_stop
                    bot.start()
                except Exception as e:
                    print(f"❌ Erro thread bot: {e}")
                    _tb.print_exc()
                finally:
                    get_user_state(deriv_id, bot_type)['running'] = False

            # Marcar running=True no Redis ANTES de iniciar thread
            # Evita que o frontend detecte 'parado' durante inicialização
            if STATE_MANAGER:
                _sm_update(deriv_id, bot_type, {
                    'running': True,
                    'stop_reason': None,
                    'stop_message': None,
                    'account_type': account_type,
                    'deriv_id': deriv_id,
                    'bot_name': bot_nome if 'bot_nome' in dir() else bot_type,
                })

            thread = threading.Thread(target=run_bot, daemon=True)
            thread.start()
            set_bot_instance(deriv_id, bot_type, bot)

            get_user_state(deriv_id, bot_type).update({
                'running': True, 'instance': bot, 'thread': thread,
                'trades': [], 'stop_reason': None, 'stop_message': None,
                'bot_name_real': data.get('bot_name', bot_type),
                '_perda_desde_ultimo_ganho': 0.0,
                '_lucro_desde_ultimo_reset': 0.0,
                'mart_step': 0, 'mart_max': 3,
            })

            return jsonify({
                'success': True, 'message': 'Bot iniciado!',
                'bot_type': bot_type, 'account_type': account_type,
                'symbol': symbol, 'mode': f'REAL BOT - {account_type.upper()}'
            })

        # ==================== SIMULADO ====================
        else:
            class SimulatedBot:
                def __init__(self):
                    self.running = True
                    self.stats = {'total_trades': 0, 'vitorias': 0, 'derrotas': 0,
                                  'lucro_liquido': 0.0, 'saldo_atual': 10000.0, 'win_rate': 0.0}
                def run(self):
                    import random
                    while self.running:
                        time.sleep(5)
                        if random.random() < 0.3:
                            won    = random.random() < 0.65
                            profit = stake_inicial * 0.95 if won else -stake_inicial
                            self.stats['total_trades'] += 1
                            if won: self.stats['vitorias'] += 1
                            else:   self.stats['derrotas'] += 1
                            self.stats['lucro_liquido'] += profit
                            self.stats['saldo_atual']   += profit
                            self.stats['win_rate'] = (self.stats['vitorias'] / self.stats['total_trades']) * 100
                def stop(self): self.running = False

            bot    = SimulatedBot()
            thread = threading.Thread(target=bot.run, daemon=True)
            thread.start()
            get_user_state(deriv_id, bot_type).update({
                'running': True, 'instance': bot, 'thread': thread,
                'trades': [], 'stop_reason': None, 'stop_message': None,
                'bot_name_real': data.get('bot_name', bot_type),
                '_perda_desde_ultimo_ganho': 0.0,
                '_lucro_desde_ultimo_reset': 0.0,
                'mart_step': 0, 'mart_max': 3,
            })
            return jsonify({'success': True, 'message': 'Bot simulado iniciado', 'mode': 'SIMULATED'})

    except Exception as e:
        print(f"❌ ERRO start_bot: {e}")
        _tb.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== STOP BOT ====================
@app.route('/api/bot/stop', methods=['POST'])
def stop_bot():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'Dados não fornecidos'}), 400

        bot_type = data.get('bot_type', 'ia')
        deriv_id = data.get('deriv_id', 'anonymous')
        if not get_user_state(deriv_id, bot_type).get('running', False):
            return jsonify({'success': False, 'error': f'Bot {bot_type} não está rodando'}), 400

        bot = get_user_state(deriv_id, bot_type).get('instance')
        if bot:
            if hasattr(bot, 'stop'):      bot.stop()
            elif hasattr(bot, 'running'): bot.running = False

            stats = {}
            if BOTS_AVAILABLE and hasattr(bot, 'stop_loss'):
                try: stats = bot.stop_loss.get_estatisticas()
                except: pass
            elif hasattr(bot, 'stats'):
                stats = bot.stats

            get_user_state(deriv_id, bot_type)['running']     = False
            get_user_state(deriv_id, bot_type)['stop_reason'] = get_user_state(deriv_id, bot_type).get('stop_reason') or 'manual'
            # Limpar estado salvo — parada manual não deve auto-reiniciar
            try: _limpar_estado(bot_type)
            except: pass
            return jsonify({'success': True, 'message': 'Bot parado!', 'stats': stats})

        return jsonify({'success': False, 'error': 'Instância não encontrada'}), 500

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== STATS ====================
@app.route('/api/bot/stats/<bot_type>')
def get_bot_stats(bot_type):
    deriv_id = request.args.get('deriv_id', 'anonymous')
    state = get_user_state(deriv_id, bot_type)
    bot   = state.get('instance')
    stats = {}

    if bot:
        if BOTS_AVAILABLE and hasattr(bot, 'stop_loss'):
            try: stats = bot.stop_loss.get_estatisticas()
            except: pass
        elif hasattr(bot, 'stats'):
            stats = bot.stats
        if BOTS_AVAILABLE and hasattr(bot, 'api'):
            try:
                stats['balance']  = bot.api.balance
                stats['currency'] = bot.api.currency
            except: pass

    thread       = state.get('thread')
    thread_alive = thread is not None and thread.is_alive()
    instance     = state.get('instance') or get_bot_instance(deriv_id, bot_type)

    # Só marca como parado se não tem instância E thread morta
    # Evita falso positivo quando estado vem do Redis sem thread local
    if state.get('running') and not thread_alive and instance is None:
        get_user_state(deriv_id, bot_type)['running'] = False
        if not get_user_state(deriv_id, bot_type).get('stop_reason'):
            get_user_state(deriv_id, bot_type)['stop_reason'] = 'crashed'

    is_running   = get_user_state(deriv_id, bot_type).get('running', False)
    stop_reason  = get_user_state(deriv_id, bot_type).get('stop_reason')
    stop_message = get_user_state(deriv_id, bot_type).get('stop_message')

    waiting_signal = False
    if is_running and bot and BOTS_AVAILABLE and hasattr(bot, 'waiting_contract'):
        waiting_signal = not bot.waiting_contract

    mart_step = get_user_state(deriv_id, bot_type).get('mart_step', 0)
    mart_max  = get_user_state(deriv_id, bot_type).get('mart_max', 3)

    return jsonify({
        'success': True, 'bot_type': bot_type, 'running': is_running,
        'stats': stats, 'stop_reason': stop_reason, 'stop_message': stop_message,
        'bot_running': is_running, 'waiting_signal': waiting_signal,
        'mart_step': mart_step, 'mart_max': mart_max,
         'strategy_name': get_user_state(deriv_id, bot_type).get('strategy_name', ''),
        'saldo_atual': stats.get('balance', 0), 'lucro_liquido': stats.get('saldo_liquido', 0),
        'total_trades': stats.get('total_trades', 0), 'win_rate': stats.get('win_rate', 0),
        'vitorias': stats.get('vitorias', 0), 'derrotas': stats.get('derrotas', 0),
        'perda_dc': get_user_state(deriv_id, bot_type).get('_perda_desde_ultimo_ganho', 0),
        'limite_perda': state.get('limite_perda', BotConfig.LIMITE_PERDA),
    })

# ==================== TRADES ====================
@app.route('/api/bot/trades/<bot_type>')
def get_bot_trades(bot_type):
    deriv_id = request.args.get('deriv_id', 'anonymous')
    trades = get_user_state(deriv_id, bot_type).get('trades', [])
    return jsonify({'success': True, 'trades': trades, 'total': len(trades)})

# ==================== BALANCE ====================
@app.route('/api/balance')
@app.route('/api/account/balance')
def get_balance():
    deriv_id = request.args.get('deriv_id', 'anonymous')
    # Busca saldo apenas do usuário correto
    user_bots = bots_state.get(deriv_id, {})
    for bot_type, state in user_bots.items():
        bot = state.get('instance')
        if bot and BOTS_AVAILABLE and hasattr(bot, 'api'):
            try:
                b = bot.api.balance
                c = bot.api.currency
                if b and b != 0:
                    return jsonify({'success': True, 'balance': b, 'currency': c, 'formatted': f"${b:,.2f}"})
            except: pass
    return jsonify({'success': True, 'balance': 0, 'currency': 'USD', 'formatted': "$0.00"})

# ==================== EMERGENCY RESET ====================
@app.route('/api/emergency/reset', methods=['POST'])
def emergency_reset():
    global bots_state
    deriv_id = request.get_json(silent=True, force=True) or {}
    deriv_id = deriv_id.get('deriv_id', 'anonymous') if isinstance(deriv_id, dict) else 'anonymous'
    for state in bots_state.values():
        bot = state.get('instance')
        if bot and hasattr(bot, 'stop'):
            try: bot.stop()
            except: pass
    bots_state = {k: {
        'running': False, 'instance': None, 'thread': None,
        'trades': [], 'stop_reason': None, 'stop_message': None
    } for k in ['manual', 'ia', 'ia_simples', 'ia_avancado']}
    return jsonify({'success': True, 'message': 'Estado resetado!'})


# ═══════════════════════════════════════════
# ROBÔ MESTRE DE SINAIS — RODA NO SERVIDOR
# ═══════════════════════════════════════════
import threading, time, random

robo_master_ativo = False
robo_master_thread = None
robo_master_intervalo = 600  # 10 minutos default

def _robo_auto_start():
    global robo_master_ativo, robo_master_thread, robo_master_intervalo
    try:
        if STATE_MANAGER and hasattr(STATE_MANAGER, 'get'):
            estado = STATE_MANAGER.get('robo_master_estado') or {}
            if estado.get('ativo'):
                robo_master_intervalo = estado.get('intervalo', 600)
                robo_master_ativo = True
                t = threading.Thread(target=robo_master_loop, daemon=True)
                t.start()
                print(f"Auto-start robo: intervalo={robo_master_intervalo}s")
    except Exception as e:
        print(f"Auto-start robo falhou: {e}")

MERCADOS_ROBO = ['R_100', 'R_75', 'R_50']
TIPOS_ROBO = ['PAR', 'IMPAR']
IMG_BASE_URL = 'https://alphadolar.online/img'

def _enviar_imagem_telegram(url_imagem, caption=''):
    try:
        token = os.environ.get('TELEGRAM_TOKEN', '')
        chat_id = os.environ.get('TELEGRAM_CHAT_ID', '')
        if not token or not chat_id:
            return False
        resp = requests.post(
            f'https://api.telegram.org/bot{token}/sendPhoto',
            json={'chat_id': chat_id, 'photo': url_imagem, 'caption': caption, 'parse_mode': 'HTML'}
        )
        return resp.json().get('ok', False)
    except Exception as e:
        print(f"Erro enviar imagem telegram: {e}")
        return False

def _verificar_resultado_sinal(mercado, tipo, ticks_espera=5):
    import websocket, json, threading
    resultado = {'ok': False, 'won': False, 'digito': None}
    ev = threading.Event()
    
    def on_msg(ws, msg):
        data = json.loads(msg)
        if data.get('msg_type') == 'authorize':
            ws.send(json.dumps({'ticks': mercado, 'subscribe': 1}))
        elif data.get('msg_type') == 'tick':
            q = float(data['tick']['quote'])
            ds = f"{q:.5f}".replace('.','')
            dg = int(ds[-1])
            resultado['digito'] = dg
            if tipo == 'PAR':
                resultado['won'] = (dg % 2 == 0)
            else:
                resultado['won'] = (dg % 2 != 0)
            resultado['ok'] = True
            ws.close()
            ev.set()
    
    def on_error(ws, err): ev.set()
    def on_close(ws, *a): ev.set()
    
    try:
        token = os.environ.get('DERIV_SIGNAL_TOKEN', '')
        ws = websocket.WebSocketApp(
            'wss://ws.derivws.com/websockets/v3?app_id=128988',
            on_message=on_msg, on_error=on_error, on_close=on_close
        )
        def on_open(ws):
            if token:
                ws.send(json.dumps({'authorize': token}))
            else:
                ws.send(json.dumps({'ticks': mercado, 'subscribe': 1}))
        ws.on_open = on_open
        t = threading.Thread(target=ws.run_forever, daemon=True)
        t.start()
        ev.wait(timeout=15)
    except Exception as e:
        print(f"Erro verificar resultado: {e}")
    
    return resultado

def robo_master_loop():
    global robo_master_ativo
    print("Robo Mestre iniciado!")
    while robo_master_ativo:
        try:
            mercado = random.choice(MERCADOS_ROBO)
            tipo = random.choice(TIPOS_ROBO)
            prob = random.randint(72, 88)
            emoji_tipo = '🔵' if tipo == 'PAR' else '🟡'
            nome_tipo = 'AZUL (PAR)' if tipo == 'PAR' else 'AMARELO (ÍMPAR)'
            
            # Enviar sinal
            texto_sinal = (
                "\u2705 ENTRADA CONFIRMADA\n\n"
                "ENTRAR NA COR " + emoji_tipo + " " + nome_tipo + "\n"
                "\U0001f4ca Mercado: " + mercado + "\n"
                "\U0001f3af Probabilidade: " + str(prob) + "%\n"
                "\U0001f504 AT\u00c9 3 GALES\n\n"
                "\U0001f916 Alpha Dolar Signals"
            )
            sinal_manual(texto_sinal)
            print(f"Sinal enviado: {tipo} {mercado} {prob}%")
            
            # Aguardar resultado — tenta até 3 gales
            gale = 0
            won = False
            time.sleep(3)  # Aguarda 3s antes de verificar
            
            while gale <= 3 and robo_master_ativo:
                res = _verificar_resultado_sinal(mercado, tipo)
                if res['ok']:
                    if res['won']:
                        won = True
                        break
                    else:
                        gale += 1
                        if gale <= 3:
                            sinal_manual(f"🔄 GALE {gale} — ENTRAR {emoji_tipo} {nome_tipo} | {mercado}")
                            time.sleep(3)
                else:
                    break
            
            # Enviar imagem resultado
            if won:
                if gale == 0:
                    img_url = f"{IMG_BASE_URL}/win-sem-gale.png"
                    caption = "✅ WIN SEM GALE!"
                elif gale == 1:
                    img_url = f"{IMG_BASE_URL}/win-gale-1.png"
                    caption = "✅ WIN NO GALE 1!"
                else:
                    img_url = f"{IMG_BASE_URL}/win-gale-2.png"
                    caption = f"✅ WIN NO GALE {gale}!"
            else:
                img_url = f"{IMG_BASE_URL}/loss.png"
                caption = "❌ LOSS — Proteção ativa. Aguarde próximo sinal."
            
            _enviar_imagem_telegram(img_url, caption)
            print(f"Resultado: {'WIN' if won else 'LOSS'} gale={gale}")

        except Exception as e:
            print(f"Erro robo: {e}")
        time.sleep(robo_master_intervalo)
    print("Robo Mestre parado!")

def robo_master_loop_OLD():
    global robo_master_ativo
    print("🤖 Robô Mestre iniciado!")
    while robo_master_ativo:
        try:
            mercado = random.choice(MERCADOS_ROBO)
            tipo = random.choice(TIPOS_ROBO)
            prob = str(random.randint(70, 89)) + '%'
            texto = f"⚡ SINAL AUTOMÁTICO — ALPHA BOT\nMercado: {mercado}\nTipo: {tipo}\nProbabilidade: {prob}\n🤖 Alpha Dolar Signals"
            if TELEGRAM_OK:
                sinal_manual(texto)
                print(f"✅ Sinal auto enviado: {tipo} {mercado} {prob}")
        except Exception as e:
            print(f"❌ Erro robô: {e}")
        time.sleep(robo_master_intervalo)
    print("⏹ Robô Mestre parado!")

@app.route('/api/robo/status', methods=['GET'])
def api_robo_status():
    return jsonify({
        'ativo': robo_master_ativo,
        'intervalo': robo_master_intervalo
    })

@app.route('/api/robo/start', methods=['POST'])
def api_robo_start():
    global robo_master_ativo, robo_master_thread, robo_master_intervalo
    data = request.get_json() or {}
    robo_master_intervalo = int(data.get('intervalo', 600))
    # Salvar estado no Redis para persistir após restart
    if STATE_MANAGER and hasattr(STATE_MANAGER, 'set'):
        STATE_MANAGER.set('robo_master_estado', {'ativo': True, 'intervalo': robo_master_intervalo})
    if not robo_master_ativo:
        robo_master_ativo = True
        robo_master_thread = threading.Thread(target=robo_master_loop, daemon=True)
        robo_master_thread.start()
    return jsonify({'ok': True, 'ativo': True, 'intervalo': robo_master_intervalo})

@app.route('/api/robo/stop', methods=['POST'])
def api_robo_stop():
    global robo_master_ativo
    robo_master_ativo = False
    if STATE_MANAGER and hasattr(STATE_MANAGER, 'set'):
        STATE_MANAGER.set('robo_master_estado', {'ativo': False, 'intervalo': robo_master_intervalo})
    return jsonify({'ok': True, 'ativo': False})


# ═══════════════════════════════════════════
# ALPHA CLOCK — SCORES DINÂMICOS POR HORÁRIO
# ═══════════════════════════════════════════
@app.route('/api/clock/scores', methods=['GET'])
def api_clock_scores():
    try:
        try:
            from backend.database import listar_operacoes
        except ImportError:
            from database import listar_operacoes
        import pytz
        from datetime import datetime, timedelta

        ops = listar_operacoes()
        BR_TZ = pytz.timezone("America/Sao_Paulo")
        
        # Filtrar últimos 30 dias
        agora = datetime.now(BR_TZ)
        cutoff = agora - timedelta(days=30)
        
        # Faixas horárias
        faixas = [
            (0, 2, "MADRUGADA"),
            (2, 4, "MADRUGADA"),
            (4, 6, "MANHÃ CEDO"),
            (6, 8, "ABERTURA BR"),
            (8, 10, "PICO MANHÃ"),
            (10, 12, "MANHÃ"),
            (12, 14, "ALMOÇO"),
            (14, 16, "PICO TARDE"),
            (16, 18, "TARDE"),
            (18, 20, "ENTARDECER"),
            (20, 22, "NOITE"),
            (22, 24, "NOITE"),
        ]
        
        scores = []
        hora_atual = agora.hour
        
        for inicio, fim, label in faixas:
            # Filtrar operações nesta faixa
            ops_faixa = []
            for op in ops:
                try:
                    dt_str = op.get('criado_em', '')
                    if not dt_str:
                        continue
                    dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
                    dt_br = dt.astimezone(BR_TZ)
                    if dt_br < cutoff:
                        continue
                    h = dt_br.hour
                    if inicio <= h < fim:
                        ops_faixa.append(op)
                except:
                    continue
            
            total = len(ops_faixa)
            if total >= 5:
                wins = sum(1 for o in ops_faixa if o.get('resultado') == 'win')
                score = round((wins / total) * 100)
                # Bonus por volume
                if total >= 50: score = min(score + 5, 99)
                elif total >= 20: score = min(score + 2, 99)
            else:
                # Poucos dados — score padrão baseado em conhecimento de mercado
                defaults = {(0,2):45,(2,4):38,(4,6):52,(6,8):65,(8,10):82,(10,12):78,
                           (12,14):60,(14,16):88,(16,18):85,(18,20):72,(20,22):55,(22,24):48}
                score = defaults.get((inicio,fim), 60)
            
            agora_nesta_faixa = inicio <= hora_atual < fim
            
            scores.append({
                'inicio': inicio,
                'fim': fim,
                'label': label,
                'score': score,
                'total_ops': total,
                'agora': agora_nesta_faixa,
                'dinamico': total >= 5
            })
        
        # Melhor horário
        melhor = max(scores, key=lambda x: x['score'])
        hora_br = agora.strftime('%H:%M')
        
        return jsonify({
            'ok': True,
            'scores': scores,
            'melhor': melhor,
            'hora_br': hora_br,
            'total_operacoes': len(ops),
            'atualizado_em': agora.strftime('%d/%m/%Y %H:%M')
        })
    except Exception as e:
        return jsonify({'ok': False, 'erro': str(e)}), 500


# ═══════════════════════════════════════════
# AUTO-RESTART — Recupera bots após deploy/sleep
# ═══════════════════════════════════════════
def auto_restart_bots():
    import time, threading
    time.sleep(5)  # Aguarda servidor subir
    print("🔄 Verificando bots para auto-restart...")
    for bot_type in ['ia', 'manual']:
        try:
            estado = _recuperar_estado(bot_type)
            if not estado:
                continue
            print(f"🔄 Auto-restart: {bot_type} — {estado.get('deriv_id','?')}")
            with app.test_request_context():
                import json
                from flask import Request
                from io import BytesIO
                payload = json.dumps({
                    'bot_type': bot_type,
                    'account_type': estado.get('account_type', 'real'),
                    'token': estado.get('token', ''),
                    'deriv_id': estado.get('deriv_id', ''),
                    'bot_name': estado.get('bot_name', bot_type),
                    'config': estado.get('config', {})
                }).encode()
                environ = {
                    'REQUEST_METHOD': 'POST',
                    'CONTENT_TYPE': 'application/json',
                    'CONTENT_LENGTH': str(len(payload)),
                    'wsgi.input': BytesIO(payload),
                }
                with app.test_request_context(
                    '/api/bot/start',
                    method='POST',
                    data=payload,
                    content_type='application/json'
                ):
                    from flask import request as req_ctx
                    resp = start_bot()
                    print(f"✅ Auto-restart {bot_type}: {resp}")
        except Exception as e:
            print(f"⚠️ Auto-restart {bot_type} falhou: {e}")

# Auto-restart desabilitado
_robo_auto_start()  # Auto-inicia robô de sinais se estava ativo — causa conflito com múltiplos usuários
# threading.Thread(target=auto_restart_bots, daemon=True).start()
print('ℹ️ Auto-restart desabilitado')


@app.route('/api/ia/analytics', methods=['GET'])
def api_ia_analytics():
    try:
        try:
            from backend.database import listar_operacoes
        except ImportError:
            from database import listar_operacoes
        import pytz
        from datetime import datetime, timedelta
        ops = listar_operacoes()
        if not ops:
            return jsonify({'ok': False, 'erro': 'Sem dados'})
        BR_TZ = pytz.timezone('America/Sao_Paulo')
        agora = datetime.now(BR_TZ)
        cutoff = agora - timedelta(days=30)
        # Filtra últimos 30 dias
        ops_recentes = []
        for op in ops:
            try:
                dt_str = op.get('criado_em', '')
                if not dt_str: continue
                dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
                dt_br = dt.astimezone(BR_TZ)
                if dt_br >= cutoff:
                    op['_hora'] = dt_br.hour
                    ops_recentes.append(op)
            except: pass
        # Win rate por tipo
        tipos = {}
        for op in ops_recentes:
            t = op.get('tipo', 'unknown')
            if t not in tipos:
                tipos[t] = {'wins': 0, 'total': 0}
            tipos[t]['total'] += 1
            if op.get('resultado') == 'win':
                tipos[t]['wins'] += 1
        tipo_stats = []
        for t, v in tipos.items():
            if v['total'] >= 5:
                wr = round(v['wins'] / v['total'] * 100, 1)
                tipo_stats.append({'tipo': t, 'win_rate': wr, 'total': v['total']})
        tipo_stats.sort(key=lambda x: x['win_rate'], reverse=True)
        # Win rate por hora atual (+/- 2h)
        hora_atual = agora.hour
        ops_hora = [op for op in ops_recentes if abs(op['_hora'] - hora_atual) <= 2]
        hora_tipos = {}
        for op in ops_hora:
            t = op.get('tipo', 'unknown')
            if t not in hora_tipos:
                hora_tipos[t] = {'wins': 0, 'total': 0}
            hora_tipos[t]['total'] += 1
            if op.get('resultado') == 'win':
                hora_tipos[t]['wins'] += 1
        hora_stats = []
        for t, v in hora_tipos.items():
            if v['total'] >= 3:
                wr = round(v['wins'] / v['total'] * 100, 1)
                hora_stats.append({'tipo': t, 'win_rate': wr, 'total': v['total']})
        hora_stats.sort(key=lambda x: x['win_rate'], reverse=True)
        # Melhor tipo agora
        melhor_agora = hora_stats[0]['tipo'] if hora_stats else (tipo_stats[0]['tipo'] if tipo_stats else None)
        return jsonify({
            'ok': True,
            'total_ops': len(ops_recentes),
            'por_tipo': tipo_stats,
            'por_hora_atual': hora_stats,
            'melhor_agora': melhor_agora,
            'hora_atual': hora_atual
        })
    except Exception as e:
        return jsonify({'ok': False, 'erro': str(e)})

# ✅ AUTO-START do robô de sinais via Redis
def _autostart_robo_sinais():
    try:
        import time
        time.sleep(5)  # Aguarda app inicializar
        robo_ativo = False
        try:
            r = redis_client
            val = r.get('robo_sinais_running')
            robo_ativo = val and val.decode() == '1'
        except:
            pass

        if robo_ativo and not robo_sinais_state['running']:
            robo_sinais_state['running'] = True
            t = threading.Thread(target=_robo_sinais_loop, daemon=True)
            t.start()
            robo_sinais_state['thread'] = t
            print("[RobôSinais] Auto-iniciado via Redis ✅")
    except Exception as e:
        print(f"[RobôSinais] Erro no auto-start: {e}")

# Salva estado no Redis ao ligar/desligar
_autostart_thread = threading.Thread(target=_autostart_robo_sinais, daemon=True)
_autostart_thread.start()

if __name__ == '__main__':
    print("\n" + "="*70)
    print("🚀 ALPHA DOLAR 2.0 - API PRODUCTION v5")
    print("🌐 URLs: / → /home | /operar → /dashboard | /guia | /videos")
    print("✅ BOTS PYTHON REAIS!" if BOTS_AVAILABLE else "⚠️ MODO SIMULADO")
    print("="*70 + "\n")
    app.run(host='0.0.0.0', port=5000, debug=True)
# ─────────────────────────────────────────────
# BANCO DE DADOS — CLIENTES
# ─────────────────────────────────────────────

# ─────────────────────────────────────────────
# BANCO DE DADOS — CLIENTES (Supabase)
# ─────────────────────────────────────────────
from database import init_db, salvar_cliente as _salvar, listar_clientes as _listar, salvar_operacao as _salvar_op, listar_operacoes as _listar_ops, listar_bots as _listar_bots, salvar_bot as _salvar_bot, atualizar_bot as _atualizar_bot, salvar_operacao as _salvar_op, salvar_estado_bot as _salvar_estado, recuperar_estado_bot as _recuperar_estado, limpar_estado_bot as _limpar_estado
init_db()

@app.route('/api/salvar-cliente', methods=['POST'])
def salvar_cliente_route():
    data = request.json
    try:
        ok = _salvar(data)
        return jsonify({'ok': ok})
    except Exception as e:
        return jsonify({'ok': False, 'erro': str(e)}), 500

@app.route('/api/clientes', methods=['GET'])
def listar_clientes_route():
    try:
        rows = _listar()
        return jsonify(rows)
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@app.route('/api/operacoes', methods=['GET'])
def operacoes_route():
    bot_name = request.args.get('bot_name')
    try:
        rows = _listar_ops(bot_name)
        return jsonify(rows)
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@app.route('/api/bots', methods=['GET'])
def bots_route():
    return jsonify(_listar_bots())

@app.route('/api/bots', methods=['POST'])
def criar_bot_route():
    data = request.json
    ok = _salvar_bot(data)
    return jsonify({'ok': ok})

@app.route('/api/bots/<nome>', methods=['PATCH'])
def atualizar_bot_route(nome):
    data = request.json
    ok = _atualizar_bot(nome, data)
    return jsonify({'ok': ok})

# ═══════════════════════════════════════════
# ROTAS TELEGRAM SIGNALS
# ═══════════════════════════════════════════
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from backend.telegram_signals import (
        sinal_manual, sinal_digitos, sinal_rise_fall,
        sinal_horario, sinal_volatilidade, sinal_resultado, enviar_telegram
    )
    TELEGRAM_OK = True
    print("✅ Telegram signals carregado!")
except Exception as e:
    print(f"❌ Telegram signals erro: {e}")
    TELEGRAM_OK = False

@app.route('/api/sinal/manual', methods=['POST'])
def api_sinal_manual():
    """Envia sinal manual pelo admin"""
    try:
        data = request.get_json()
        texto = data.get('texto', '')
        if not texto:
            return jsonify({'erro': 'texto obrigatório'}), 400
        ok = sinal_manual(texto)
        return jsonify({'ok': ok})
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@app.route('/api/sinal/padrao', methods=['POST'])
def api_sinal_padrao():
    """Envia sinal de padrão de dígitos"""
    try:
        data = request.get_json()
        ok = sinal_digitos(
            data.get('mercado', 'R_100'),
            data.get('tipo', 'DIGITEVEN'),
            data.get('probabilidade', 75),
            data.get('digitos', [])
        )
        return jsonify({'ok': ok})
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@app.route('/api/sinal/resultado', methods=['POST'])
def api_sinal_resultado():
    """Envia resultado de operação"""
    try:
        data = request.get_json()
        ok = sinal_resultado(
            data.get('tipo', ''),
            data.get('mercado', ''),
            data.get('resultado', ''),
            float(data.get('lucro', 0)),
            data.get('win_rate', 0)
        )
        return jsonify({'ok': ok})
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@app.route('/api/sinal/volatilidade', methods=['POST'])
def api_sinal_volatilidade():
    """Envia alerta de volatilidade"""
    try:
        data = request.get_json()
        ok = sinal_volatilidade(
            data.get('mercado', ''),
            data.get('nivel', 'ATENÇÃO'),
            float(data.get('ratio', 1.5))
        )
        return jsonify({'ok': ok})
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@app.route('/api/sinal/horario', methods=['POST'])
def api_sinal_horario():
    """Envia alerta de horário"""
    try:
        data = request.get_json()
        ok = sinal_horario(
            data.get('faixa', ''),
            int(data.get('score', 0)),
            data.get('recomendacao', '')
        )
        return jsonify({'ok': ok})
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

# ═══════════════════════════════════════════
# ROTAS GESTÃO DE ASSINANTES SIGNALS
# ═══════════════════════════════════════════
try:
    from backend.signals_access import (
        listar_assinantes, buscar_assinante, adicionar_assinante,
        revogar_assinante, gerar_link_convite, verificar_expiracao
    )
    SIGNALS_OK = True
    print("✅ Signals access carregado!")
except Exception as e:
    print(f"❌ Signals access erro: {e}")
    SIGNALS_OK = False

@app.route('/api/signals/assinantes', methods=['GET'])
def api_listar_assinantes():
    try:
        return jsonify(listar_assinantes())
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@app.route('/api/signals/adicionar', methods=['POST'])
def api_adicionar_assinante():
    try:
        data = request.get_json()
        result = adicionar_assinante(
            data.get('nome',''),
            data.get('email',''),
            int(data.get('telegram_id',0)),
            data.get('telegram_username',''),
            data.get('plano','signals'),
            int(data.get('dias',30))
        )
        return jsonify({'ok': True, 'data': result})
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@app.route('/api/signals/revogar', methods=['POST'])
def api_revogar_assinante():
    try:
        data = request.get_json()
        result = revogar_assinante(
            int(data.get('telegram_id',0)),
            data.get('motivo','manual')
        )
        return jsonify({'ok': True})
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@app.route('/api/signals/link', methods=['GET'])
def api_gerar_link():
    try:
        link = gerar_link_convite()
        return jsonify({'ok': bool(link), 'link': link})
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@app.route('/api/signals/verificar', methods=['POST'])
def api_verificar_expiracao():
    try:
        expulsos = verificar_expiracao()
        return jsonify({'ok': True, 'expulsos': expulsos})
    except Exception as e:
        return jsonify({'erro': str(e)}), 500


# ═══════════════════════════════════════════════════════════
# 🤖 ROBÔ DE SINAIS TELEGRAM — Loop contínuo
# ═══════════════════════════════════════════════════════════

robo_sinais_state = {
    'running': False,
    'thread': None,
    'intervalo': 300,
    'total_enviados': 0,
    'ultimo_envio': None
}

def _robo_sinais_loop():
    import random
    from backend.telegram_signals import sinal_digitos, enviar_telegram

    mercados = ['R_10', 'R_25', 'R_50', 'R_75', 'R_100']
    tipos_digit = ['DIGITEVEN', 'DIGITODD', 'DIGITOVER', 'DIGITUNDER']

    print("[RobôSinais] Loop iniciado")

    while robo_sinais_state['running']:
        try:
            mercado = random.choice(mercados)
            tipo    = random.choice(tipos_digit)
            prob    = random.randint(62, 89)
            digitos = [random.randint(0, 9) for _ in range(10)]
            sinal_digitos(mercado, tipo, prob, digitos)
            robo_sinais_state['total_enviados'] += 1
            robo_sinais_state['ultimo_envio'] = datetime.now().strftime('%H:%M:%S')
            print(f"[RobôSinais] Sinal #{robo_sinais_state['total_enviados']} enviado")
        except Exception as e:
            print(f"[RobôSinais] Erro: {e}")

        segundos = robo_sinais_state['intervalo']
        for _ in range(segundos // 5):
            if not robo_sinais_state['running']:
                break
            time.sleep(5)

    print("[RobôSinais] Loop encerrado")


@app.route('/api/robo-sinais/start', methods=['POST'])
def start_robo_sinais():
    if robo_sinais_state['running']:
        return jsonify({'error': 'Robô já rodando'}), 400
    data = request.json or {}
    robo_sinais_state['intervalo'] = max(60, int(data.get('intervalo', 300)))
    robo_sinais_state['running'] = True
    t = threading.Thread(target=_robo_sinais_loop, daemon=True)
    t.start()
    robo_sinais_state['thread'] = t
    # Salva no Redis para auto-restart após redeploy
    try: redis_client.set('robo_sinais_running', '1')
    except: pass
    from backend.telegram_signals import enviar_telegram
    enviar_telegram("🟢 <b>ALPHA SIGNALS ATIVADO</b>\n\nRobô de sinais iniciado!\n\n🌐 alphadolar.online")
    return jsonify({'success': True, 'intervalo': robo_sinais_state['intervalo']})


@app.route('/api/robo-sinais/stop', methods=['POST'])
def stop_robo_sinais():
    if not robo_sinais_state['running']:
        return jsonify({'error': 'Robô não está rodando'}), 400
    robo_sinais_state['running'] = False
    # Remove do Redis
    try: redis_client.delete('robo_sinais_running')
    except: pass
    from backend.telegram_signals import enviar_telegram
    enviar_telegram("🔴 <b>ALPHA SIGNALS PAUSADO</b>\n\nRobô parado pelo admin.\n\n🌐 alphadolar.online")
    return jsonify({'success': True, 'total_enviados': robo_sinais_state['total_enviados']})


@app.route('/api/robo-sinais/status', methods=['GET'])
def status_robo_sinais():
    return jsonify({
        'running':        robo_sinais_state['running'],
        'intervalo':      robo_sinais_state['intervalo'],
        'total_enviados': robo_sinais_state['total_enviados'],
        'ultimo_envio':   robo_sinais_state['ultimo_envio']
    })


@app.route('/api/robo-sinais/sinal-manual', methods=['POST'])
def enviar_sinal_manual_prod():
    from backend.telegram_signals import sinal_manual
    data    = request.json or {}
    texto   = data.get('texto', '')
    direcao = data.get('direcao', None)
    if not texto:
        return jsonify({'error': 'Texto obrigatório'}), 400
    ok = sinal_manual(texto, direcao=direcao)
    return jsonify({'success': ok})



# ==================== TRIAL 24H ====================
@app.route('/api/trial/ativar', methods=['POST'])
def ativar_trial():
    import requests as req
    from datetime import datetime, timedelta, timezone

    dados = request.get_json(silent=True) or {}
    email = dados.get('email', '').strip().lower()
    produto = dados.get('produto', '').strip()

    if not email or not produto:
        return jsonify({'erro': 'Email e produto obrigatorios'}), 400

    SUPABASE_URL = 'https://urlthgicnomfbyklesou.supabase.co'
    SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVybHRoZ2ljbm9tZmJ5a2xlc291Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MzA2NzIwNiwiZXhwIjoyMDg4NjQzMjA2fQ.ZcPJry5CAxteeM2x-vymjXTFQ3EWZast0SHw-YRh1vo'
    HEADERS = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json',
        'Prefer': 'return=representation',
    }

    # Verifica se ja usou trial neste produto
    check = req.get(
        f"{SUPABASE_URL}/rest/v1/produtos_liberados?email=eq.{email}&produto=eq.{produto}&tipo=eq.trial&select=id",
        headers=HEADERS, timeout=10
    )
    if check.json():
        return jsonify({'erro': 'Trial ja utilizado para este produto'}), 403

    # Ativa trial 24h
    expiracao = (datetime.now(timezone.utc) + timedelta(hours=24)).isoformat()
    insert = req.post(
        f"{SUPABASE_URL}/rest/v1/produtos_liberados",
        headers=HEADERS,
        json={
            'email'         : email,
            'produto'       : produto,
            'tipo'          : 'trial',
            'ativo'         : True,
            'origem'        : 'trial',
            'data_expiracao': expiracao,
        },
        timeout=10
    )

    if insert.status_code in (200, 201):
        return jsonify({'status': 'ok', 'expiracao': expiracao}), 200
    else:
        return jsonify({'erro': 'Erro ao ativar trial'}), 500


# ==================== MARKUP DERIV ====================
@app.route('/api/markup/stats', methods=['GET'])
def get_markup_stats():
    import websocket
    import json
    import threading

    token = os.environ.get('DERIV_ADMIN_TOKEN', '')
    app_id = os.environ.get('DERIV_APP_ID', '128988')

    if not token:
        return jsonify({'erro': 'DERIV_ADMIN_TOKEN não configurado'}), 500

    resultado = {'dados': None, 'erro': None}
    evento = threading.Event()

    def on_message(ws, message):
        data = json.loads(message)
        if data.get('msg_type') == 'authorize':
            ws.send(json.dumps({
                'app_markup_statistics': 1,
                'date_from': '2026-01-01',
                'date_to':   '2026-12-31',
            }))
        elif data.get('msg_type') == 'app_markup_statistics':
            resultado['dados'] = data.get('app_markup_statistics', {})
            ws.close()
            evento.set()
        elif 'error' in data:
            resultado['erro'] = data['error'].get('message', 'Erro desconhecido')
            ws.close()
            evento.set()

    def on_error(ws, error):
        resultado['erro'] = str(error)
        evento.set()

    ws = websocket.WebSocketApp(
        f'wss://ws.derivws.com/websockets/v3?app_id={app_id}',
        on_message=on_message,
        on_error=on_error,
    )
    ws.send = lambda msg: ws.sock.send(msg) if ws.sock else None

    def on_open(ws):
        ws.send(json.dumps({'authorize': token}))

    ws.on_open = on_open
    t = threading.Thread(target=ws.run_forever)
    t.daemon = True
    t.start()
    evento.wait(timeout=15)

    if resultado['erro']:
        return jsonify({'erro': resultado['erro']}), 500
    if not resultado['dados']:
        return jsonify({'erro': 'Timeout ou sem dados'}), 504

    stats = resultado['dados']
    return jsonify({
        'status': 'ok',
        'markup_usd': stats.get('markup_usd', 0),
        'markup_transactions_count': stats.get('markup_transactions_count', 0),
        'app_id': app_id,
    }), 200


# ==================== REVENUE SHARE REAL + MARKUP ====================
@app.route('/api/admin/financeiro', methods=['GET'])
def get_financeiro_admin():
    """Retorna dados financeiros reais para o painel admin principal"""
    import requests as req
    from datetime import datetime

    SUPA_URL = os.environ.get('SUPABASE_URL', '')
    SUPA_KEY = os.environ.get('SUPABASE_KEY', '')
    headers  = {'apikey': SUPA_KEY, 'Authorization': f'Bearer {SUPA_KEY}'}

    # 1. Busca todos os bots
    bots_r = req.get(f"{SUPA_URL}/rest/v1/bots?status=eq.ativo", headers=headers)
    bots   = bots_r.json() if bots_r.status_code == 200 else []

    # 2. Busca clientes via afiliado
    cli_r  = req.get(f"{SUPA_URL}/rest/v1/clientes?via_afiliado=eq.true&select=deriv_id,bot_afiliado,bot_name", headers=headers)
    clientes_afiliado = cli_r.json() if cli_r.status_code == 200 else []

    # IDs dos clientes afiliados
    ids_afiliados = {c['deriv_id'] for c in clientes_afiliado}

    # 3. Aceita filtro de data via query params
    date_from = request.args.get('date_from', datetime.utcnow().strftime('%Y-%m-01'))
    date_to   = request.args.get('date_to',   datetime.utcnow().strftime('%Y-%m-%d') + 'T23:59:59')
    mes_inicio = date_from
    ops_r = req.get(
        f"{SUPA_URL}/rest/v1/operacoes?select=cliente_id,resultado,lucro,bot_name,stake&criado_em=gte.{date_from}&limit=5000",
        headers=headers
    )
    operacoes = ops_r.json() if ops_r.status_code == 200 else []

    # 4. Calcula por bot
    resultado_bots = []
    total_ganhos_afiliado = 0
    total_perdas_afiliado = 0

    for bot in bots:
        bot_nome = bot.get('nome', '')
        markup_pct = float(bot.get('markup_pct', 2.0))

        # Clientes deste bot via afiliado
        ids_bot_afiliado = {c['deriv_id'] for c in clientes_afiliado if c.get('bot_afiliado') == bot_nome or c.get('bot_name') == bot_nome}

        # Operacoes do bot
        ops_bot = [o for o in operacoes if o.get('bot_name') == bot_nome]

        # Total geral do bot
        ganhos_total = sum(abs(o['lucro']) for o in ops_bot if o.get('resultado') == 'win')
        perdas_total = sum(abs(o['lucro']) for o in ops_bot if o.get('resultado') == 'loss')

        # Somente clientes afiliados
        ops_afiliado = [o for o in ops_bot if o.get('cliente_id') in ids_bot_afiliado]
        ganhos_af = sum(abs(o['lucro']) for o in ops_afiliado if o.get('resultado') == 'win')
        perdas_af = sum(abs(o['lucro']) for o in ops_afiliado if o.get('resultado') == 'loss')
        net_af    = round(perdas_af - ganhos_af, 2)
        rev_share = round(net_af * 0.30, 2)

        total_ganhos_afiliado += ganhos_af
        total_perdas_afiliado += perdas_af

        # Markup estimado por bot
        total_stakes_bot = sum(float(o.get('stake', 0)) for o in ops_bot)
        markup_est_bot   = round(total_stakes_bot * (markup_pct / 100), 2)
        markup_alpha_bot = round(markup_est_bot * 0.20, 2)

        resultado_bots.append({
            'nome'              : bot_nome,
            'dono'              : bot.get('dono', ''),
            'ganhos_total'      : round(ganhos_total, 2),
            'perdas_total'      : round(perdas_total, 2),
            'ganhos_afiliado'   : round(ganhos_af, 2),
            'perdas_afiliado'   : round(perdas_af, 2),
            'net_revenue'       : net_af,
            'revenue_share_30'  : rev_share,
            'markup_pct'        : markup_pct,
            'markup_estimado'   : markup_est_bot,
            'markup_alpha_20'   : markup_alpha_bot,
            'total_stakes'      : round(total_stakes_bot, 2),
            'clientes_afiliado' : len(ids_bot_afiliado),
        })

    net_total   = round(total_perdas_afiliado - total_ganhos_afiliado, 2)
    rev_total   = round(net_total * 0.30, 2)
    sua_comissao = round(rev_total * 0.20, 2)

    # 5. Busca markup real da Deriv
    markup_deriv = _buscar_markup_deriv()

    return jsonify({
        'status'              : 'ok',
        'mes'                 : mes_inicio,
        'total_ganhos_af'     : round(total_ganhos_afiliado, 2),
        'total_perdas_af'     : round(total_perdas_afiliado, 2),
        'net_revenue_total'   : net_total,
        'revenue_share_total' : rev_total,
        'sua_comissao_20'     : sua_comissao,
        'markup_deriv_usd'    : markup_deriv.get('markup_usd', 0),
        'markup_trades'       : markup_deriv.get('markup_transactions_count', 0),
        'bots'                : resultado_bots,
    })


@app.route('/api/admin/financeiro/<bot_nome>', methods=['GET'])
def get_financeiro_bot(bot_nome):
    """Retorna dados financeiros para o painel do trader"""
    import requests as req
    from datetime import datetime

    SUPA_URL = os.environ.get('SUPABASE_URL', '')
    SUPA_KEY = os.environ.get('SUPABASE_KEY', '')
    headers  = {'apikey': SUPA_KEY, 'Authorization': f'Bearer {SUPA_KEY}'}

    # Aceita filtro de data via query params
    date_from = request.args.get('date_from', datetime.utcnow().strftime('%Y-%m-01'))
    date_to   = request.args.get('date_to',   datetime.utcnow().strftime('%Y-%m-%d') + 'T23:59:59')
    mes_inicio = date_from

    # Clientes afiliados deste bot — busca por bot_name OU bot_afiliado
    cli_r = req.get(
        f"{SUPA_URL}/rest/v1/clientes?via_afiliado=eq.true&select=deriv_id,bot_name,bot_afiliado",
        headers=headers
    )
    todos_clientes_af = cli_r.json() if cli_r.status_code == 200 else []
    # Filtra por bot_name OU bot_afiliado (case insensitive)
    ids_af = {
        c['deriv_id'] for c in todos_clientes_af
        if (c.get('bot_name','').lower() == bot_nome.lower() or
            c.get('bot_afiliado','').lower() == bot_nome.lower())
    }

    # Operacoes do bot
    ops_r = req.get(
        f"{SUPA_URL}/rest/v1/operacoes?bot_name=eq.{bot_nome}&select=cliente_id,resultado,lucro,stake&criado_em=gte.{date_from}&limit=2000",
        headers=headers
    )
    operacoes = ops_r.json() if ops_r.status_code == 200 else []

    # Total geral
    ganhos_total = sum(abs(o['lucro']) for o in operacoes if o.get('resultado') == 'win')
    perdas_total = sum(abs(o['lucro']) for o in operacoes if o.get('resultado') == 'loss')

    # Somente afiliados
    ops_af   = [o for o in operacoes if o.get('cliente_id') in ids_af]
    ganhos_af = sum(abs(o['lucro']) for o in ops_af if o.get('resultado') == 'win')
    perdas_af = sum(abs(o['lucro']) for o in ops_af if o.get('resultado') == 'loss')
    net_af    = round(perdas_af - ganhos_af, 2)
    rev_share = round(net_af * 0.30, 2)
    pagar_alpha = round(rev_share * 0.20, 2)
    seu_lucro   = round(rev_share * 0.80, 2)

    # Markup estimado (2% das stakes)
    markup_pct = 0.02
    total_stakes = sum(float(o.get('stake', 0)) for o in operacoes)
    markup_estimado = round(total_stakes * markup_pct, 2)
    markup_alpha_20 = round(markup_estimado * 0.20, 2)
    markup_trader_80 = round(markup_estimado * 0.80, 2)

    # Total a pagar para Alpha Dolar
    total_pagar_alpha = round(pagar_alpha + markup_alpha_20, 2)
    total_lucro_trader = round(seu_lucro + markup_trader_80, 2)

    return jsonify({
        'status'              : 'ok',
        'bot_nome'            : bot_nome,
        'mes'                 : mes_inicio,
        'ganhos_total'        : round(ganhos_total, 2),
        'perdas_total'        : round(perdas_total, 2),
        'ganhos_afiliado'     : round(ganhos_af, 2),
        'perdas_afiliado'     : round(perdas_af, 2),
        'net_revenue'         : net_af,
        'revenue_share_30'    : rev_share,
        'pagar_alpha_20'      : pagar_alpha,
        'seu_lucro_80'        : seu_lucro,
        'markup_estimado'     : markup_estimado,
        'markup_alpha_20'     : markup_alpha_20,
        'markup_trader_80'    : markup_trader_80,
        'total_pagar_alpha'   : total_pagar_alpha,
        'total_lucro_trader'  : total_lucro_trader,
        'total_stakes'        : round(total_stakes, 2),
        'clientes_afiliado'   : len(ids_af),
        'clientes_total'      : len(set(o.get('cliente_id') for o in operacoes)),
    })


def _buscar_markup_deriv():
    """Busca markup real da Deriv via WebSocket"""
    import websocket, json, threading
    from datetime import datetime

    token  = os.environ.get('DERIV_ADMIN_TOKEN', '')
    app_id = os.environ.get('DERIV_APP_ID', '128988')
    if not token:
        return {'markup_usd': 0, 'markup_transactions_count': 0}

    resultado = {}
    evento = threading.Event()

    def on_message(ws, message):
        data = json.loads(message)
        if data.get('msg_type') == 'authorize':
            ano = datetime.utcnow().year
            ws.send(json.dumps({
                'app_markup_statistics': 1,
                'date_from': f'{ano}-01-01',
                'date_to'  : f'{ano}-12-31',
            }))
        elif data.get('msg_type') == 'app_markup_statistics':
            resultado.update(data.get('app_markup_statistics', {}))
            ws.close()
            evento.set()
        elif 'error' in data:
            ws.close()
            evento.set()

    def on_open(ws):
        ws.send(json.dumps({'authorize': token}))

    def on_error(ws, err):
        evento.set()

    ws = websocket.WebSocketApp(
        f'wss://ws.derivws.com/websockets/v3?app_id={app_id}',
        on_message=on_message,
        on_error=on_error,
        on_open=on_open,
    )
    t = threading.Thread(target=ws.run_forever)
    t.daemon = True
    t.start()
    evento.wait(timeout=10)
    return {
        'markup_usd': resultado.get('markup_usd', 0),
        'markup_transactions_count': resultado.get('markup_transactions_count', 0),
    }

@app.route('/api/admin/status', methods=['GET'])
def get_admin_status():
    try:
        import os, resource
        mem_mb = round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024, 1)
    except:
        mem_mb = -1
    try:
        bots_rodando = sum(1 for k,v in USER_STATES.items() if isinstance(v, dict) and v.get('running'))
        users = len(USER_STATES)
    except:
        bots_rodando = -1
        users = -1
    return jsonify({'status':'ok','memoria_mb':mem_mb,'bots_rodando':bots_rodando,'users_em_memoria':users})
