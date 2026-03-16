import sys
import os
import threading
import time
import traceback as _tb
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

# ==================== IMPORTAR BOTS ====================

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
# bots_state agora é isolado por usuário: bots_state[deriv_id][bot_type]
bots_state = {}

def get_user_state(deriv_id, bot_type):
    """Retorna ou cria estado isolado por usuário"""
    if not deriv_id:
        deriv_id = 'anonymous'
    if deriv_id not in bots_state:
        bots_state[deriv_id] = {}
    if bot_type not in bots_state[deriv_id]:
        bots_state[deriv_id][bot_type] = {
            'running': False, 'instance': None, 'thread': None,
            'trades': [], 'stop_reason': None, 'stop_message': None
        }
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
        stake_inicial = float(config.get('stake_inicial', 0.35))
        lucro_alvo    = float(config.get('lucro_alvo', 2.0))
        limite_perda  = float(config.get('limite_perda', 5.0))

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
                bot_cadastrado = next((b for b in bots if b.get('deriv_id') == deriv_id), None)
                bot_nome = bot_cadastrado['nome'] if bot_cadastrado else data.get('bot_name', f'BOT {deriv_id}')
            except:
                bot_nome = data.get('bot_name', bot_type)
            get_user_state(deriv_id, bot_type)['bot_name'] = bot_nome
            print(f"🔑 Token [{account_type.upper()}]: {token[:10]}...")

            trading_mode   = config.get('trading_mode', 'faster')
            risk_mode      = config.get('risk_mode', 'conservative')
            strategy_id    = config.get('strategy', 'alpha_bot_1')
            stop_loss_type = config.get('stop_loss_type', 'value')
            max_losses     = int(config.get('max_losses', 5))

            BotConfig.STOP_LOSS_TYPE         = stop_loss_type
            BotConfig.MAX_CONSECUTIVE_LOSSES = max_losses
            BotConfig.STAKE_INICIAL = float(config.get('stake') or config.get('stake_inicial') or BotConfig.STAKE_INICIAL)
            BotConfig.LUCRO_ALVO    = float(config.get('target') or config.get('lucro_alvo') or BotConfig.LUCRO_ALVO)
            BotConfig.LIMITE_PERDA  = float(config.get('stop') or config.get('limite_perda') or 1000.0)

            try:
                factory  = STRATEGY_MAP.get(strategy_id, STRATEGY_MAP['alpha_bot_1'])
                strategy = factory(trading_mode, risk_mode)
            except Exception as e:
                return jsonify({'success': False, 'error': f'Erro estratégia: {str(e)}'}), 500

            try:
                bot = AlphaDolar(strategy=strategy, use_martingale=getattr(strategy, "usar_martingale", True))
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

            def on_trade_completed(direction, won, profit, stake, symbol_used, exit_tick=None):
                print(f"🔔 on_trade_completed CHAMADO! won={won} profit={profit} step_antes={get_user_state(deriv_id, bot_type).get('mart_step',0)}")
                try:
                    _cliente_id = next(iter([v.get('deriv_id','') for v in [bots_state.get(bot_type,{})] if v.get('deriv_id')]), '')
                    _bot_name = get_user_state(deriv_id, bot_type).get('bot_name_real', bot_type)
                    _salvar_op(_bot_name, _cliente_id, direction, won, profit, stake)
                except: pass
                trades_ate_agora = get_user_state(deriv_id, bot_type)['trades']
                total = len(trades_ate_agora) + 1
                wins  = sum(1 for t in trades_ate_agora if t.get('result') == 'win') + (1 if won else 0)
                wr    = round((wins / total) * 100, 1) if total > 0 else 0

                if hasattr(bot, "atualizar_apos_trade"): bot.atualizar_apos_trade(won, profit)
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
                limite   = BotConfig.LIMITE_PERDA

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
                get_user_state(deriv_id, bot_type)['trades'].append(trade)
                if len(get_user_state(deriv_id, bot_type)['trades']) > 100:
                    get_user_state(deriv_id, bot_type)['trades'].pop(0)
                # Salvar operação no Supabase (somente conta REAL)
                try:
                    if get_user_state(deriv_id, bot_type).get('account_type', 'demo') == 'real':
                        cliente_id = get_user_state(deriv_id, bot_type).get('deriv_id', '') or get_user_state(deriv_id, bot_type).get('cliente_id', '')
                        _salvar_op(
                            bot_name=get_user_state(deriv_id, bot_type).get('bot_name', bot_type),
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

            thread = threading.Thread(target=run_bot, daemon=True)
            thread.start()

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

    if state.get('running') and not thread_alive:
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
    for bot_type, state in bots_state.items():
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

MERCADOS_ROBO = ['R_100', 'R_75', 'R_50']
TIPOS_ROBO = ['PAR', 'ÍMPAR', 'CALL', 'PUT']

def robo_master_loop():
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
    if not robo_master_ativo:
        robo_master_ativo = True
        robo_master_thread = threading.Thread(target=robo_master_loop, daemon=True)
        robo_master_thread.start()
    return jsonify({'ok': True, 'ativo': True, 'intervalo': robo_master_intervalo})

@app.route('/api/robo/stop', methods=['POST'])
def api_robo_stop():
    global robo_master_ativo
    robo_master_ativo = False
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

# Iniciar auto-restart em thread separada
threading.Thread(target=auto_restart_bots, daemon=True).start()


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
