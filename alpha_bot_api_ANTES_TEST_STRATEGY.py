# VERSÃO ATUALIZADA 2026-01-02 04:45
"""
ALPHA DOLAR 2.0 - API PRODUCTION INTEGRADA
API Flask que conecta frontend web com bots Python reais
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import threading
import time
from datetime import datetime
import sys
import os

# Adiciona path dos bots
project_path = os.path.dirname(os.path.abspath(__file__))
backend_path = os.path.join(project_path, 'backend')
sys.path.insert(0, project_path)
sys.path.insert(0, backend_path)

app = Flask(__name__, static_folder='web', static_url_path='')
CORS(app)

# ==================== IMPORTAR BOTS REAIS ====================

try:
    from backend.bot import AlphaDolar
    from backend.config import BotConfig
    from backend.strategies.alpha_bot_1 import AlphaBot1
    BOTS_AVAILABLE = True
    print("✅ Bots Python carregados com sucesso!")
except ImportError as e:
    BOTS_AVAILABLE = False
    print(f"⚠️ Erro ao importar bots: {e}")
    print("   Sistema funcionará em modo simulado apenas")

# ==================== ESTADO GLOBAL ====================

bots_state = {
    'manual': {'running': False, 'instance': None, 'thread': None},
    'ia': {'running': False, 'instance': None, 'thread': None},
    'ia_simples': {'running': False, 'instance': None, 'thread': None},
    'ia_avancado': {'running': False, 'instance': None, 'thread': None}
}

# Configuração global
global_config = {
    'symbol': 'R_100',
    'contract_type': 'CALL',
    'stake_inicial': 1.0,
    'lucro_alvo': 50.0,
    'limite_perda': 100.0
}

# ==================== ROTAS ESTÁTICAS ====================

@app.route('/')
def index():
    return send_from_directory('web', 'trading.html')

@app.route('/<path:path>')
def serve_static(path):
    try:
        return send_from_directory('web', path)
    except:
        return jsonify({'error': 'Not found'}), 404

# ==================== ROTAS API ====================

@app.route('/api/health')
def health():
    return jsonify({
        'status': 'ok',
        'message': 'Alpha Dolar API Running',
        'bots_available': BOTS_AVAILABLE
    })

@app.route('/api/bots/status')
def get_bots_status():
    status = {}
    for bot_type, state in bots_state.items():
        bot_instance = state.get('instance')
        status[bot_type] = {
            'running': state['running'],
            'stats': {}
        }

        # Se bot real está rodando, pega estatísticas
        if BOTS_AVAILABLE and bot_instance and hasattr(bot_instance, 'stop_loss'):
            try:
                stats = bot_instance.stop_loss.get_estatisticas()
                status[bot_type]['stats'] = stats
            except:
                pass

    return jsonify(status)

@app.route('/api/bot/start', methods=['POST'])
def start_bot():
    """Iniciar bot - VERSÃO INTEGRADA COM BOTS REAIS"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                'success': False,
                'error': 'Dados não fornecidos'
            }), 400

        bot_type = data.get('bot_type', 'manual')
        config = data.get('config', {})

        print(f"\n{'='*60}")
        print(f"📥 Recebido pedido para iniciar bot: {bot_type}")
        print(f"⚙️ Config recebida: {config}")
        print(f"{'='*60}\n")

        # Verificar se bot_type existe
        if bot_type not in bots_state:
            bots_state[bot_type] = {'running': False, 'instance': None, 'thread': None}

        # Verificar se já está rodando
        if bots_state[bot_type].get('running', False):
            return jsonify({
                'success': False,
                'error': f'Bot {bot_type} já está rodando'
            }), 400

        # ==================== INICIAR BOT REAL ====================

        if BOTS_AVAILABLE and bot_type in ['ia', 'ia_simples']:
            print("🤖 Iniciando BOT PYTHON REAL...")

            # Aplicar configurações
            BotConfig.DEFAULT_SYMBOL = config.get('symbol', 'R_100')
            BotConfig.STAKE_INICIAL = config.get('stake_inicial', 1.0)
            BotConfig.LUCRO_ALVO = config.get('lucro_alvo', 20.0)
            BotConfig.LIMITE_PERDA = config.get('limite_perda', 1000.0)

            # Selecionar estratégia
            strategy_id = config.get('strategy', 'alpha_bot_1')

            try:
                # Por enquanto, sempre usa AlphaBot1
                # TODO: Implementar seleção dinâmica de estratégias
                strategy = AlphaBot1()
                print(f"✅ Estratégia carregada: {strategy.name}")
            except Exception as e:
                print(f"❌ Erro ao carregar estratégia: {e}")
                return jsonify({
                    'success': False,
                    'error': f'Erro ao carregar estratégia: {str(e)}'
                }), 500

            # Criar bot
            try:
                use_martingale = config.get('martingale', False)
                bot = AlphaDolar(
                    strategy=strategy,
                    use_martingale=use_martingale
                )
                print(f"✅ Bot criado: {bot.bot_name}")
            except Exception as e:
                print(f"❌ Erro ao criar bot: {e}")
                return jsonify({
                    'success': False,
                    'error': f'Erro ao criar bot: {str(e)}'
                }), 500

            # Iniciar em thread separada
            def run_bot():
                try:
                    print(f"🚀 Thread do bot iniciada")
                    bot.start()
                except Exception as e:
                    print(f"❌ Erro na thread do bot: {e}")
                    import traceback
                    traceback.print_exc()
                    bots_state[bot_type]['running'] = False

            thread = threading.Thread(target=run_bot, daemon=True)
            thread.start()

            # Salvar estado
            bots_state[bot_type] = {
                'running': True,
                'instance': bot,
                'thread': thread
            }

            print(f"✅ Bot {bot_type} iniciado com sucesso!")

            return jsonify({
                'success': True,
                'message': f'Bot {bot_type} iniciado com BOT REAL!',
                'bot_type': bot_type,
                'config': {
                    'symbol': BotConfig.DEFAULT_SYMBOL,
                    'stake_inicial': BotConfig.STAKE_INICIAL,
                    'lucro_alvo': BotConfig.LUCRO_ALVO,
                    'limite_perda': BotConfig.LIMITE_PERDA,
                    'strategy': strategy.name
                },
                'mode': 'REAL BOT'
            })

        # ==================== FALLBACK: MODO SIMULADO ====================

        else:
            print("⚠️ Bots não disponíveis, usando modo simulado...")

            # Criar simulação simples
            class SimulatedBot:
                def __init__(self, bot_type, config):
                    self.bot_type = bot_type
                    self.config = config
                    self.running = True
                    self.stats = {
                        'total_trades': 0,
                        'vitorias': 0,
                        'derrotas': 0,
                        'lucro_liquido': 0.0,
                        'saldo_atual': 10000.0,
                        'win_rate': 0.0
                    }

                def run(self):
                    import random
                    while self.running:
                        time.sleep(5)
                        # Simula trade
                        if random.random() < 0.3:
                            won = random.random() < 0.65
                            stake = self.config.get('stake_inicial', 1.0)
                            profit = stake * 0.95 if won else -stake

                            self.stats['total_trades'] += 1
                            if won:
                                self.stats['vitorias'] += 1
                            else:
                                self.stats['derrotas'] += 1

                            self.stats['lucro_liquido'] += profit
                            self.stats['saldo_atual'] += profit

                            if self.stats['total_trades'] > 0:
                                self.stats['win_rate'] = (self.stats['vitorias'] / self.stats['total_trades']) * 100

                            print(f"{'✅' if won else '❌'} Trade simulado: ${profit:+.2f}")

                def stop(self):
                    self.running = False

            bot = SimulatedBot(bot_type, config)

            def run_simulated():
                bot.run()

            thread = threading.Thread(target=run_simulated, daemon=True)
            thread.start()

            bots_state[bot_type] = {
                'running': True,
                'instance': bot,
                'thread': thread
            }

            return jsonify({
                'success': True,
                'message': f'Bot {bot_type} iniciado em MODO SIMULADO',
                'bot_type': bot_type,
                'config': config,
                'mode': 'SIMULATED'
            })

    except Exception as e:
        print(f"❌ ERRO em start_bot: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        }), 500

@app.route('/api/bot/stop', methods=['POST'])
def stop_bot():
    """Parar bot"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                'success': False,
                'error': 'Dados não fornecidos'
            }), 400

        bot_type = data.get('bot_type', 'ia')

        print(f"🛑 Parando bot: {bot_type}")

        if bot_type not in bots_state:
            return jsonify({
                'success': False,
                'error': f'Bot {bot_type} não encontrado'
            }), 400

        if not bots_state[bot_type].get('running', False):
            return jsonify({
                'success': False,
                'error': f'Bot {bot_type} não está rodando'
            }), 400

        bot = bots_state[bot_type].get('instance')

        if bot:
            # Parar bot
            if hasattr(bot, 'stop'):
                bot.stop()
            elif hasattr(bot, 'running'):
                bot.running = False

            # Pegar estatísticas finais
            stats = {}
            if BOTS_AVAILABLE and hasattr(bot, 'stop_loss'):
                try:
                    stats = bot.stop_loss.get_estatisticas()
                except:
                    pass
            elif hasattr(bot, 'stats'):
                stats = bot.stats

            bots_state[bot_type]['running'] = False

            print(f"✅ Bot {bot_type} parado")

            return jsonify({
                'success': True,
                'message': f'Bot {bot_type} parado com sucesso!',
                'stats': stats
            })

        return jsonify({
            'success': False,
            'error': 'Instância do bot não encontrada'
        }), 500

    except Exception as e:
        print(f"❌ ERRO em stop_bot: {e}")
        return jsonify({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        }), 500

@app.route('/api/config', methods=['GET', 'POST'])
def config():
    if request.method == 'GET':
        return jsonify(global_config)

    try:
        data = request.get_json()
        if data:
            global_config.update(data)
            return jsonify({'success': True, 'config': global_config})
        return jsonify({'success': False, 'error': 'Dados inválidos'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/stats')
def get_stats():
    """Estatísticas globais"""
    total_stats = {
        'total_trades': 0,
        'vitorias': 0,
        'derrotas': 0,
        'lucro_liquido': 0.0,
        'saldo_atual': 10000.0,
        'win_rate': 0.0
    }

    for bot_type, state in bots_state.items():
        bot = state.get('instance')
        if bot:
            if BOTS_AVAILABLE and hasattr(bot, 'stop_loss'):
                try:
                    stats = bot.stop_loss.get_estatisticas()
                    total_stats['total_trades'] += stats.get('total_trades', 0)
                    total_stats['vitorias'] += stats.get('vitorias', 0)
                    total_stats['derrotas'] += stats.get('derrotas', 0)
                    total_stats['lucro_liquido'] += stats.get('saldo_liquido', 0.0)
                except:
                    pass
            elif hasattr(bot, 'stats'):
                stats = bot.stats
                total_stats['total_trades'] += stats.get('total_trades', 0)
                total_stats['vitorias'] += stats.get('vitorias', 0)
                total_stats['derrotas'] += stats.get('derrotas', 0)
                total_stats['lucro_liquido'] += stats.get('lucro_liquido', 0.0)

    if total_stats['total_trades'] > 0:
        total_stats['win_rate'] = (total_stats['vitorias'] / total_stats['total_trades']) * 100

    return jsonify(total_stats)

@app.route('/api/balance')
def get_balance():
    """Retorna saldo atual da conta Deriv"""
    for bot_type, state in bots_state.items():
        bot = state.get('instance')
        if bot and BOTS_AVAILABLE and hasattr(bot, 'api'):
            try:
                balance = bot.api.balance
                currency = bot.api.currency
                return jsonify({
                    'success': True,
                    'balance': balance,
                    'currency': currency,
                    'formatted': f"${balance:,.2f}"
                })
            except:
                pass

    return jsonify({
        'success': True,
        'balance': 9999.00,
        'currency': 'USD',
        'formatted': "$9,999.00"
    })

@app.route('/api/bot/stats/<bot_type>')
def get_bot_stats(bot_type):
    """Retorna estatísticas de um bot específico"""
    if bot_type not in bots_state:
        return jsonify({'success': False, 'error': 'Bot não encontrado'}), 404

    state = bots_state[bot_type]
    bot = state.get('instance')

    if not bot:
        return jsonify({'success': False, 'error': 'Bot não está rodando'}), 400

    stats = {}

    if BOTS_AVAILABLE and hasattr(bot, 'stop_loss'):
        try:
            stats = bot.stop_loss.get_estatisticas()
        except:
            pass
    elif hasattr(bot, 'stats'):
        stats = bot.stats

    if BOTS_AVAILABLE and hasattr(bot, 'api'):
        try:
            stats['balance'] = bot.api.balance
            stats['currency'] = bot.api.currency
        except:
            pass

    return jsonify({
        'success': True,
        'bot_type': bot_type,
        'running': state.get('running', False),
        'stats': stats
    })

# ==================== EXECUTAR ====================

if __name__ == '__main__':
    print("\n" + "=" * 70)
    print("🚀 ALPHA DOLAR 2.0 - API PRODUCTION")
    if BOTS_AVAILABLE:
        print("✅ BOTS PYTHON REAIS INTEGRADOS!")
    else:
        print("⚠️ MODO SIMULADO (Bots Python não disponíveis)")
    print("=" * 70)
    print("🌐 http://localhost:5000")
    print("=" * 70 + "\n")

    app.run(host='0.0.0.0', port=5000, debug=True)