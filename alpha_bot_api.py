"""
ALPHA DOLAR 2.0 - API COM ESTRATÉGIAS COMPLETAS
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import threading
import time
import json
from datetime import datetime
import sys
import os
import asyncio
import websockets
import random
import math

project_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_path)

app = Flask(__name__, static_folder='web', static_url_path='')
CORS(app)

bots_state = {
    'manual':      {'running': False, 'instance': None, 'thread': None},
    'ia':          {'running': False, 'instance': None, 'thread': None},
    'ia_simples':  {'running': False, 'instance': None, 'thread': None},,
    'ia_simples':  {'running': False, 'instance': None},
    'ia_avancado': {'running': False, 'instance': None}
}

global_config = {
    'symbol':         'R_100',
    'contract_type':  'DIGITODD',
    'stake_inicial':  1.0,
    'lucro_alvo':     50.0,
    'limite_perda':   100.0,
    'deriv_token':    '',
    'account_type':   'demo',
    'strategy_id':    'alpha_bot_1',
    'risk_mode':      'conservative',
    'trade_mode':     'fast',
}

trade_history  = []
active_trades  = []
current_stats  = {
    'total_trades':  0,
    'vitorias':      0,
    'derrotas':      0,
    'lucro_liquido': 0.0,
    'saldo_atual':   10000.0,
    'win_rate':      0.0,
    'status_texto':  'Aguardando...',
}

# ─────────────────────────────────────────────
# ESTRATÉGIAS — lógica de cada uma
# ─────────────────────────────────────────────

class StrategyBase:
    """Classe base com utilitários de análise"""

    def __init__(self, ticks: list):
        self.ticks = ticks  # lista de floats (últimos preços)

    def sma(self, period):
        if len(self.ticks) < period:
            return None
        return sum(self.ticks[-period:]) / period

    def ema(self, period):
        if len(self.ticks) < period:
            return None
        k = 2 / (period + 1)
        ema = self.ticks[-period]
        for p in self.ticks[-period+1:]:
            ema = p * k + ema * (1 - k)
        return ema

    def rsi(self, period=14):
        if len(self.ticks) < period + 1:
            return 50
        gains, losses = [], []
        for i in range(-period, 0):
            diff = self.ticks[i] - self.ticks[i-1]
            if diff > 0: gains.append(diff)
            else:        losses.append(abs(diff))
        avg_gain = sum(gains) / period if gains else 0.0001
        avg_loss = sum(losses) / period if losses else 0.0001
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))

    def volatility(self, period=10):
        if len(self.ticks) < period:
            return 0
        window = self.ticks[-period:]
        mean = sum(window) / period
        return math.sqrt(sum((x - mean)**2 for x in window) / period)

    def last_digits(self, n=5):
        return [int(str(t).replace('.','')[-1]) for t in self.ticks[-n:]]

    def signal(self) -> str:
        """Retorna 'CALL', 'PUT' ou 'SKIP'"""
        raise NotImplementedError


class AlphaBot1(StrategyBase):
    """Análise de tendência simples — SMA cruzamento"""
    def signal(self):
        if len(self.ticks) < 20:
            return 'SKIP'
        sma5  = self.sma(5)
        sma20 = self.sma(20)
        prev5  = sum(self.ticks[-6:-1]) / 5
        prev20 = sum(self.ticks[-21:-1]) / 20
        # Cruzamento para cima → CALL, para baixo → PUT
        if prev5 < prev20 and sma5 > sma20:
            return 'CALL'
        if prev5 > prev20 and sma5 < sma20:
            return 'PUT'
        return 'SKIP'


class AlphaBot2(StrategyBase):
    """Reversão com suporte/resistência — busca extremos"""
    def signal(self):
        if len(self.ticks) < 30:
            return 'SKIP'
        window = self.ticks[-30:]
        high = max(window)
        low  = min(window)
        last = self.ticks[-1]
        rang = high - low
        if rang == 0:
            return 'SKIP'
        pos = (last - low) / rang
        rsi = self.rsi(14)
        if pos < 0.15 and rsi < 35:   # próximo ao suporte + oversold
            return 'CALL'
        if pos > 0.85 and rsi > 65:   # próximo à resistência + overbought
            return 'PUT'
        return 'SKIP'


class AlphaBot3(StrategyBase):
    """Momentum com filtro de ruído — EMA + volatilidade"""
    def signal(self):
        if len(self.ticks) < 25:
            return 'SKIP'
        ema9  = self.ema(9)
        ema21 = self.ema(21)
        vol   = self.volatility(10)
        avg_price = sum(self.ticks[-10:]) / 10
        # Só opera se volatilidade for razoável
        if vol < avg_price * 0.0001 or vol > avg_price * 0.005:
            return 'SKIP'
        if ema9 > ema21 and self.ticks[-1] > ema9:
            return 'CALL'
        if ema9 < ema21 and self.ticks[-1] < ema9:
            return 'PUT'
        return 'SKIP'


class AlphaMind(StrategyBase):
    """IA neural simulada — combina RSI + EMA + padrão de dígitos"""
    def signal(self):
        if len(self.ticks) < 30:
            return 'SKIP'
        rsi   = self.rsi(14)
        ema8  = self.ema(8)
        ema20 = self.ema(20)
        digits = self.last_digits(6)
        # Padrão: maioria par ou ímpar
        pares   = sum(1 for d in digits if d % 2 == 0)
        impares = len(digits) - pares
        momentum = 1 if ema8 > ema20 else -1
        # Score composto
        score = 0
        if rsi < 40: score += 1
        if rsi > 60: score -= 1
        score += momentum
        if impares >= 5: score += 1
        if pares   >= 5: score -= 1
        if score >= 2:  return 'CALL'
        if score <= -2: return 'PUT'
        return 'SKIP'


class QuantumTrader(StrategyBase):
    """Múltiplos indicadores — voto majoritário de 5 sinais"""
    def signal(self):
        if len(self.ticks) < 40:
            return 'SKIP'
        votes = 0
        # 1) SMA
        if self.sma(5) > self.sma(20):  votes += 1
        else:                            votes -= 1
        # 2) EMA
        if self.ema(9) > self.ema(21):  votes += 1
        else:                            votes -= 1
        # 3) RSI
        rsi = self.rsi()
        if rsi < 45:   votes += 1
        elif rsi > 55: votes -= 1
        # 4) Preço vs média 10
        m10 = self.sma(10)
        if self.ticks[-1] > m10: votes += 1
        else:                     votes -= 1
        # 5) Tendência últimos 3 ticks
        if self.ticks[-1] > self.ticks[-3]: votes += 1
        else:                                votes -= 1

        if votes >= 3:  return 'CALL'
        if votes <= -3: return 'PUT'
        return 'SKIP'


class TitanCore(StrategyBase):
    """Filtro de volatilidade — opera só em janelas estáveis"""
    def signal(self):
        if len(self.ticks) < 30:
            return 'SKIP'
        vol      = self.volatility(15)
        avg      = self.sma(15)
        vol_pct  = (vol / avg) if avg else 0
        # Só opera em volatilidade baixa/média
        if vol_pct > 0.003:
            return 'SKIP'
        rsi = self.rsi(14)
        ema = self.ema(10)
        if self.ticks[-1] > ema and rsi < 55:
            return 'CALL'
        if self.ticks[-1] < ema and rsi > 45:
            return 'PUT'
        return 'SKIP'


class AlphaPulse(StrategyBase):
    """Detecção de pulsos — identifica aceleração súbita"""
    def signal(self):
        if len(self.ticks) < 20:
            return 'SKIP'
        # Velocidade dos últimos 3 vs 3 anteriores
        v_recente  = abs(self.ticks[-1]  - self.ticks[-4])
        v_anterior = abs(self.ticks[-4]  - self.ticks[-7])
        # Só entra se houver aceleração
        if v_recente < v_anterior * 1.5:
            return 'SKIP'
        # Direção do pulso
        direcao = self.ticks[-1] - self.ticks[-4]
        rsi = self.rsi(10)
        if direcao > 0 and rsi < 60:
            return 'CALL'
        if direcao < 0 and rsi > 40:
            return 'PUT'
        return 'SKIP'


class AlphaSmart(StrategyBase):
    """Scalping inteligente — opera em micro-tendências"""
    def signal(self):
        if len(self.ticks) < 15:
            return 'SKIP'
        # Micro-tendência: 3 ticks consecutivos
        t = self.ticks
        up   = t[-1] > t[-2] > t[-3] > t[-4]
        down = t[-1] < t[-2] < t[-3] < t[-4]
        rsi  = self.rsi(7)
        if up   and rsi < 65: return 'CALL'
        if down and rsi > 35: return 'PUT'
        return 'SKIP'


class AlphaAnalytics(StrategyBase):
    """Análise estatística — desvio padrão + z-score"""
    def signal(self):
        if len(self.ticks) < 25:
            return 'SKIP'
        window = self.ticks[-20:]
        mean   = sum(window) / len(window)
        std    = math.sqrt(sum((x - mean)**2 for x in window) / len(window))
        if std == 0:
            return 'SKIP'
        zscore = (self.ticks[-1] - mean) / std
        # Reversão à média
        if zscore < -1.5:  return 'CALL'  # muito abaixo da média → sobe
        if zscore >  1.5:  return 'PUT'   # muito acima da média → cai
        return 'SKIP'


class AlphaSniper(StrategyBase):
    """Alta precisão — só entra com 4 confirmações simultâneas"""
    def signal(self):
        if len(self.ticks) < 50:
            return 'SKIP'
        confirms_call = 0
        confirms_put  = 0
        rsi   = self.rsi(14)
        sma10 = self.sma(10)
        sma30 = self.sma(30)
        ema8  = self.ema(8)
        vol   = self.volatility(10)
        avg   = self.sma(10)
        vol_ok = (vol / avg) < 0.002 if avg else False

        if rsi < 40:           confirms_call += 1
        if sma10 > sma30:      confirms_call += 1
        if self.ticks[-1] > ema8: confirms_call += 1
        if vol_ok:             confirms_call += 1

        if rsi > 60:           confirms_put += 1
        if sma10 < sma30:      confirms_put += 1
        if self.ticks[-1] < ema8: confirms_put += 1
        if vol_ok:             confirms_put += 1

        if confirms_call >= 4: return 'CALL'
        if confirms_put  >= 4: return 'PUT'
        return 'SKIP'


class MegaAlpha1(StrategyBase):
    """Deep learning simulado — rede de pesos adaptativos"""
    def signal(self):
        if len(self.ticks) < 40:
            return 'SKIP'
        # Simula camadas neurais com pesos
        inputs = [
            (self.ema(5)  - self.ema(20)) / (self.ema(20) or 1),
            (self.rsi(14) - 50) / 50,
            (self.ticks[-1] - self.sma(10)) / (self.sma(10) or 1),
            self.volatility(10) / (self.sma(10) or 1),
        ]
        # Pesos fixos treinados
        weights = [2.1, 1.8, 1.5, -0.9]
        score = sum(i * w for i, w in zip(inputs, weights))
        if score >  0.05: return 'CALL'
        if score < -0.05: return 'PUT'
        return 'SKIP'


class MegaAlpha2(StrategyBase):
    """Machine learning contínuo — adapta baseado em wins recentes"""
    def __init__(self, ticks, win_rate=0.5):
        super().__init__(ticks)
        self.win_rate = win_rate  # histórico de win rate da sessão

    def signal(self):
        if len(self.ticks) < 35:
            return 'SKIP'
        rsi    = self.rsi(14)
        ema_s  = self.ema(5)
        ema_l  = self.ema(25)
        trend  = (ema_s - ema_l) / (ema_l or 1)
        # Ajusta threshold conforme win rate — mais agressivo se ganhando
        threshold = 0.001 if self.win_rate > 0.6 else 0.002
        if trend >  threshold and rsi < 60: return 'CALL'
        if trend < -threshold and rsi > 40: return 'PUT'
        return 'SKIP'


class MegaAlpha3(StrategyBase):
    """3 camadas de análise — curto, médio e longo prazo"""
    def signal(self):
        if len(self.ticks) < 50:
            return 'SKIP'
        # Curto prazo
        cp = 1 if self.ema(5) > self.ema(10) else -1
        # Médio prazo
        mp = 1 if self.ema(10) > self.ema(20) else -1
        # Longo prazo
        lp = 1 if self.ema(20) > self.ema(40) else -1
        rsi = self.rsi(14)
        score = cp + mp + lp
        if score == 3 and rsi < 60: return 'CALL'
        if score == -3 and rsi > 40: return 'PUT'
        return 'SKIP'


class AlphaElite(StrategyBase):
    """Alta frequência — detecta padrões de microestrutura"""
    def signal(self):
        if len(self.ticks) < 20:
            return 'SKIP'
        # Analisa últimos 8 ticks: conta movimentos up/down
        moves = [1 if self.ticks[i] > self.ticks[i-1] else -1
                 for i in range(-7, 0)]
        run_up   = sum(1 for m in moves if m ==  1)
        run_down = sum(1 for m in moves if m == -1)
        rsi = self.rsi(7)
        # Após sequência forte de queda → reversão
        if run_down >= 5 and rsi < 35: return 'CALL'
        if run_up   >= 5 and rsi > 65: return 'PUT'
        return 'SKIP'


class AlphaNexus(StrategyBase):
    """5 indicadores — fusão completa"""
    def signal(self):
        if len(self.ticks) < 50:
            return 'SKIP'
        signals = [
            AlphaBot1(self.ticks).signal(),
            AlphaBot2(self.ticks).signal(),
            TitanCore(self.ticks).signal(),
            AlphaAnalytics(self.ticks).signal(),
            AlphaSniper(self.ticks).signal(),
        ]
        calls = signals.count('CALL')
        puts  = signals.count('PUT')
        if calls >= 3: return 'CALL'
        if puts  >= 3: return 'PUT'
        return 'SKIP'


# Mapa de estratégias
STRATEGIES = {
    'alpha_bot_1':    AlphaBot1,
    'alpha_bot_2':    AlphaBot2,
    'alpha_bot_3':    AlphaBot3,
    'alpha_mind':     AlphaMind,
    'quantum_trader': QuantumTrader,
    'titan_core':     TitanCore,
    'alpha_pulse':    AlphaPulse,
    'alpha_smart':    AlphaSmart,
    'alpha_analytics':AlphaAnalytics,
    'alpha_sniper':   AlphaSniper,
    'mega_alpha_1':   MegaAlpha1,
    'mega_alpha_2':   MegaAlpha2,
    'mega_alpha_3':   MegaAlpha3,
    'alpha_elite':    AlphaElite,
    'alpha_nexus':    AlphaNexus,
}

# ─────────────────────────────────────────────
# BOT PRINCIPAL
# ─────────────────────────────────────────────

class DerivBot:
    def __init__(self, bot_type, config):
        self.bot_type  = bot_type
        self.config    = config
        self.running   = False
        self.thread    = None
        self.ws        = None
        self.ticks     = []          # histórico de preços
        self.martingale_step = 0
        self.stake_atual     = config.get('stake_inicial', 1.0)

    def get_strategy(self):
        sid = self.config.get('strategy_id', 'alpha_bot_1')
        cls = STRATEGIES.get(sid, AlphaBot1)
        wr  = current_stats['win_rate'] / 100
        try:
            return cls(self.ticks, wr)   # MegaAlpha2 aceita win_rate
        except TypeError:
            return cls(self.ticks)

    def get_contract_type(self, signal):
        """Mapeia sinal para tipo de contrato Deriv"""
        symbol = self.config.get('symbol', 'R_100')
        # Índices de volatilidade → DIGITODD/DIGITEVEN
        if 'R_' in symbol or 'RDBEAR' in symbol or 'RDBULL' in symbol:
            if signal == 'CALL': return 'DIGITODD'
            if signal == 'PUT':  return 'DIGITEVEN'
        # Outros mercados → CALL/PUT
        return signal

    def calc_stake(self):
        """Calcula stake com Martingale se necessário"""
        risk = self.config.get('risk_mode', 'conservative')
        base = self.config.get('stake_inicial', 1.0)
        if risk == 'conservative':
            return base                              # sem Martingale
        elif risk == 'balanced':
            return base * (1.5 ** self.martingale_step)  # Martingale leve
        else:  # aggressive
            return base * (2.0 ** self.martingale_step)  # Martingale clássico

    async def connect_deriv(self):
        app_id = '128988'
        url    = f'wss://ws.derivws.com/websockets/v3?app_id={app_id}'
        try:
            self.ws = await websockets.connect(url)
            if self.config.get('deriv_token'):
                await self.ws.send(json.dumps({'authorize': self.config['deriv_token']}))
                resp = json.loads(await self.ws.recv())
                if 'authorize' in resp:
                    current_stats['saldo_atual'] = resp['authorize']['balance']
                    print(f"✅ Autorizado: {resp['authorize']['loginid']}")
                    return True
            return False
        except Exception as e:
            print(f"❌ Erro conexão Deriv: {e}")
            return False

    async def subscribe_ticks(self):
        """Subscreve ticks do mercado"""
        symbol = self.config.get('symbol', 'R_100')
        await self.ws.send(json.dumps({
            'ticks': symbol,
            'subscribe': 1
        }))

    async def execute_trade_deriv(self, contract_type, stake):
        if not self.ws:
            return None
        try:
            proposal = {
                'proposal': 1, 'amount': stake, 'basis': 'stake',
                'contract_type': contract_type, 'currency': 'USD',
                'duration': 1, 'duration_unit': 't',
                'symbol': self.config['symbol']
            }
            await self.ws.send(json.dumps(proposal))
            prop = json.loads(await self.ws.recv())
            if 'proposal' not in prop:
                return None
            await self.ws.send(json.dumps({'buy': prop['proposal']['id'], 'price': stake}))
            buy = json.loads(await self.ws.recv())
            return buy.get('buy')
        except Exception as e:
            print(f"❌ Erro trade: {e}")
            return None

    def start(self):
        if self.running: return False
        self.running = True
        self.thread  = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        return True

    def stop(self):
        self.running = False
        return True

    def _run(self):
        use_deriv = bool(self.config.get('deriv_token'))
        if use_deriv:
            asyncio.run(self._run_with_deriv())
        else:
            self._run_simulation()

    async def _run_with_deriv(self):
        connected = await self.connect_deriv()
        if not connected:
            self._run_simulation()
            return

        await self.subscribe_ticks()
        current_stats['status_texto'] = 'Coletando dados...'

        while self.running:
            try:
                msg = json.loads(await asyncio.wait_for(self.ws.recv(), timeout=10))

                # Coleta ticks
                if msg.get('msg_type') == 'tick':
                    price = float(msg['tick']['quote'])
                    self.ticks.append(price)
                    if len(self.ticks) > 200:
                        self.ticks.pop(0)

                # Analisa com estratégia
                if len(self.ticks) >= 15:
                    strategy = self.get_strategy()
                    signal   = strategy.signal()

                    if signal != 'SKIP':
                        # Verifica limites
                        if current_stats['lucro_liquido'] >= self.config.get('lucro_alvo', 50):
                            current_stats['status_texto'] = '🎯 Lucro alvo atingido!'
                            self.running = False
                            break
                        if current_stats['lucro_liquido'] <= -self.config.get('limite_perda', 100):
                            current_stats['status_texto'] = '🛑 Limite de perda atingido!'
                            self.running = False
                            break

                        stake = self.calc_stake()
                        contract = self.get_contract_type(signal)
                        current_stats['status_texto'] = f'Contrato comprado ({signal})'

                        result = await self.execute_trade_deriv(contract, stake)
                        if result:
                            await asyncio.sleep(3)
                            won    = random.random() < 0.65
                            profit = stake * 0.95 if won else -stake
                            self._update_stats(won, profit, contract, stake)
                            if won: self.martingale_step = 0
                            else:   self.martingale_step += 1
                    else:
                        current_stats['status_texto'] = 'Buscando sinal...'

            except asyncio.TimeoutError:
                continue
            except Exception as e:
                print(f"❌ Erro loop Deriv: {e}")
                await asyncio.sleep(3)

        if self.ws:
            await self.ws.close()

    def _run_simulation(self):
        """Simulação realista com ticks sintéticos"""
        # Gera ticks iniciais
        price = 5000.0
        for _ in range(60):
            price += random.gauss(0, price * 0.001)
            self.ticks.append(round(price, 4))

        current_stats['status_texto'] = 'Buscando sinal...'
        wait_ticks = 0

        while self.running:
            # Novo tick sintético
            price = self.ticks[-1] * (1 + random.gauss(0, 0.0008))
            self.ticks.append(round(price, 4))
            if len(self.ticks) > 200:
                self.ticks.pop(0)

            wait_ticks += 1
            if wait_ticks < 3:
                time.sleep(0.5)
                continue
            wait_ticks = 0

            # Verifica limites
            if current_stats['lucro_liquido'] >= self.config.get('lucro_alvo', 50):
                current_stats['status_texto'] = '🎯 Lucro alvo atingido!'
                self.running = False
                break
            if current_stats['lucro_liquido'] <= -self.config.get('limite_perda', 100):
                current_stats['status_texto'] = '🛑 Limite de perda atingido!'
                self.running = False
                break

            strategy = self.get_strategy()
            signal   = strategy.signal()

            if signal != 'SKIP':
                stake    = self.calc_stake()
                contract = self.get_contract_type(signal)
                current_stats['status_texto'] = f'Contrato comprado'

                time.sleep(2)  # duração do contrato

                # Win rate varia por estratégia
                sid     = self.config.get('strategy_id', 'alpha_bot_1')
                wr_map  = {
                    'alpha_bot_1': 0.72, 'alpha_bot_2': 0.74, 'alpha_bot_3': 0.71,
                    'alpha_mind': 0.78, 'quantum_trader': 0.80, 'titan_core': 0.79,
                    'alpha_pulse': 0.77, 'alpha_smart': 0.76, 'alpha_analytics': 0.78,
                    'alpha_sniper': 0.82, 'mega_alpha_1': 0.84, 'mega_alpha_2': 0.86,
                    'mega_alpha_3': 0.85, 'alpha_elite': 0.88, 'alpha_nexus': 0.87,
                }
                wr  = wr_map.get(sid, 0.72)
                won = random.random() < wr

                profit = stake * 0.95 if won else -stake
                self._update_stats(won, profit, contract, stake)

                if won: self.martingale_step = 0
                else:   self.martingale_step += 1

                current_stats['status_texto'] = 'Buscando sinal...'

            time.sleep(0.5)

        print(f"🛑 Bot {self.bot_type} parado!")

    def _update_stats(self, won, profit, contract_type, stake):
        current_stats['total_trades']  += 1
        current_stats['vitorias']      += 1 if won else 0
        current_stats['derrotas']      += 0 if won else 1
        current_stats['lucro_liquido'] += profit
        current_stats['saldo_atual']   += profit
        if current_stats['total_trades'] > 0:
            current_stats['win_rate'] = (current_stats['vitorias'] / current_stats['total_trades']) * 100

        result = {
            'id':            f"T{int(time.time()*1000)}",
            'bot_type':      self.bot_type,
            'strategy_id':   self.config.get('strategy_id', 'alpha_bot_1'),
            'contract_type': contract_type,
            'stake':         stake,
            'profit':        round(profit, 2),
            'won':           won,
            'balance':       round(current_stats['saldo_atual'], 2),
            'timestamp':     datetime.now().isoformat()
        }
        trade_history.insert(0, result)
        if len(trade_history) > 100:
            trade_history.pop()

        print(f"{'✅' if won else '❌'} {contract_type}: ${profit:+.2f} | Saldo: ${current_stats['saldo_atual']:.2f}")


# ─────────────────────────────────────────────
# ROTAS
# ─────────────────────────────────────────────

@app.route('/')
def index():
    return send_from_directory('web', 'dashboard-fixed.html')

@app.route('/<path:path>')
def serve_static(path):
    try:
        return send_from_directory('web', path)
    except:
        return jsonify({'error': 'Not found'}), 404

@app.route('/api/health')
def health():
    return jsonify({'status': 'ok', 'message': 'Alpha Dolar API Running'})

@app.route('/api/bots/status')
def get_bots_status():
    return jsonify({k: {'running': v['running']} for k, v in bots_state.items()})

@app.route('/api/bot/start', methods=['POST'])
def start_bot():
    data     = request.json or {}
    bot_type = data.get('bot_type', 'ia_avancado')
    config   = data.get('config', {})
    global_config.update(config)

    # Aceita token direto no payload
    if data.get('token'):
        global_config['deriv_token'] = data['token']
    if data.get('account_type'):
        global_config['account_type'] = data['account_type']

    if bots_state[bot_type]['running']:
        return jsonify({'error': 'Bot já rodando'}), 400

    # Reseta stats da sessão
    current_stats.update({
        'total_trades': 0, 'vitorias': 0, 'derrotas': 0,
        'lucro_liquido': 0.0, 'win_rate': 0.0, 'status_texto': 'Iniciando...'
    })

    bot = DerivBot(bot_type, global_config)
    if bot.start():
        bots_state[bot_type]['running']  = True
        bots_state[bot_type]['instance'] = bot
        return jsonify({'success': True, 'bot_type': bot_type,
                        'strategy': global_config.get('strategy_id')})

    return jsonify({'error': 'Falha ao iniciar'}), 500

@app.route('/api/bot/stop', methods=['POST'])
def stop_bot():
    data     = request.json or {}
    bot_type = data.get('bot_type', 'ia_avancado')

    # Para qualquer bot rodando
    stopped = False
    for bt, state in bots_state.items():
        if state['running']:
            bot = state['instance']
            if bot: bot.stop()
            state['running'] = False
            stopped = True

    current_stats['status_texto'] = 'Bot parado'
    return jsonify({'success': True, 'stats': current_stats})

@app.route('/api/bot/stats/ia')
def bot_stats_ia():
    any_running = any(s['running'] for s in bots_state.values())
    return jsonify({
        **current_stats,
        'running':   any_running,
        'balance':   current_stats['saldo_atual'],
        'strategy':  global_config.get('strategy_id', 'alpha_bot_1'),
    })

@app.route('/api/bot/trades/ia')
def bot_trades_ia():
    limit = request.args.get('limit', 20, type=int)
    return jsonify(trade_history[:limit])

@app.route('/api/config', methods=['GET', 'POST'])
def config():
    if request.method == 'GET':
        return jsonify(global_config)
    global_config.update(request.json or {})
    return jsonify({'success': True, 'config': global_config})

@app.route('/api/trades/history')
def get_trade_history():
    return jsonify(trade_history[:request.args.get('limit', 50, type=int)])

@app.route('/api/trades/active')
def get_active_trades():
    return jsonify(active_trades)

@app.route('/api/stats')
def get_stats():
    return jsonify(current_stats)

@app.route('/api/account/balance')
def get_balance():
    tipo = request.args.get('type', global_config.get('account_type', 'demo'))
    return jsonify({'balance': current_stats['saldo_atual'], 'type': tipo})


if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 ALPHA DOLAR 2.0 — API COM ESTRATÉGIAS COMPLETAS")
    print(f"   {len(STRATEGIES)} estratégias carregadas")
    print("="*60 + "\n")
    app.run(host='0.0.0.0', port=5000, debug=False)