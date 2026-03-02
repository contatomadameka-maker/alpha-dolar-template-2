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
from collections import Counter, deque

project_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_path)

app = Flask(__name__, static_folder='web', static_url_path='')
CORS(app)

bots_state = {
    'manual':      {'running': False, 'instance': None},
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
# ESTRATÉGIAS — Rise/Fall
# ─────────────────────────────────────────────

class StrategyBase:
    def __init__(self, ticks: list):
        self.ticks = ticks

    def sma(self, period):
        if len(self.ticks) < period: return None
        return sum(self.ticks[-period:]) / period

    def ema(self, period):
        if len(self.ticks) < period: return None
        k = 2 / (period + 1)
        ema = self.ticks[-period]
        for p in self.ticks[-period+1:]:
            ema = p * k + ema * (1 - k)
        return ema

    def rsi(self, period=14):
        if len(self.ticks) < period + 1: return 50
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
        if len(self.ticks) < period: return 0
        window = self.ticks[-period:]
        mean = sum(window) / period
        return math.sqrt(sum((x - mean)**2 for x in window) / period)

    def last_digits(self, n=5):
        return [int(str(t).replace('.','')[-1]) for t in self.ticks[-n:]]

    def signal(self) -> str:
        raise NotImplementedError


class AlphaBot1(StrategyBase):
    def signal(self):
        if len(self.ticks) < 20: return 'SKIP'
        sma5  = self.sma(5);  sma20 = self.sma(20)
        prev5  = sum(self.ticks[-6:-1]) / 5
        prev20 = sum(self.ticks[-21:-1]) / 20
        if prev5 < prev20 and sma5 > sma20: return 'CALL'
        if prev5 > prev20 and sma5 < sma20: return 'PUT'
        return 'SKIP'

class AlphaBot2(StrategyBase):
    def signal(self):
        if len(self.ticks) < 30: return 'SKIP'
        window = self.ticks[-30:]
        high = max(window); low = min(window); last = self.ticks[-1]
        rang = high - low
        if rang == 0: return 'SKIP'
        pos = (last - low) / rang; rsi = self.rsi(14)
        if pos < 0.15 and rsi < 35: return 'CALL'
        if pos > 0.85 and rsi > 65: return 'PUT'
        return 'SKIP'

class AlphaBot3(StrategyBase):
    def signal(self):
        if len(self.ticks) < 25: return 'SKIP'
        ema9 = self.ema(9); ema21 = self.ema(21)
        vol = self.volatility(10); avg_price = sum(self.ticks[-10:]) / 10
        if vol < avg_price * 0.0001 or vol > avg_price * 0.005: return 'SKIP'
        if ema9 > ema21 and self.ticks[-1] > ema9: return 'CALL'
        if ema9 < ema21 and self.ticks[-1] < ema9: return 'PUT'
        return 'SKIP'

class AlphaMind(StrategyBase):
    def signal(self):
        if len(self.ticks) < 30: return 'SKIP'
        rsi = self.rsi(14); ema8 = self.ema(8); ema20 = self.ema(20)
        digits = self.last_digits(6)
        pares = sum(1 for d in digits if d % 2 == 0)
        impares = len(digits) - pares
        momentum = 1 if ema8 > ema20 else -1
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
    def signal(self):
        if len(self.ticks) < 40: return 'SKIP'
        votes = 0
        if self.sma(5) > self.sma(20):          votes += 1
        else:                                     votes -= 1
        if self.ema(9) > self.ema(21):           votes += 1
        else:                                     votes -= 1
        rsi = self.rsi()
        if rsi < 45:   votes += 1
        elif rsi > 55: votes -= 1
        m10 = self.sma(10)
        if self.ticks[-1] > m10: votes += 1
        else:                     votes -= 1
        if self.ticks[-1] > self.ticks[-3]: votes += 1
        else:                                votes -= 1
        if votes >= 3:  return 'CALL'
        if votes <= -3: return 'PUT'
        return 'SKIP'

class TitanCore(StrategyBase):
    def signal(self):
        if len(self.ticks) < 30: return 'SKIP'
        vol = self.volatility(15); avg = self.sma(15)
        vol_pct = (vol / avg) if avg else 0
        if vol_pct > 0.003: return 'SKIP'
        rsi = self.rsi(14); ema = self.ema(10)
        if self.ticks[-1] > ema and rsi < 55: return 'CALL'
        if self.ticks[-1] < ema and rsi > 45: return 'PUT'
        return 'SKIP'

class AlphaPulse(StrategyBase):
    def signal(self):
        if len(self.ticks) < 20: return 'SKIP'
        v_recente  = abs(self.ticks[-1] - self.ticks[-4])
        v_anterior = abs(self.ticks[-4] - self.ticks[-7])
        if v_recente < v_anterior * 1.5: return 'SKIP'
        direcao = self.ticks[-1] - self.ticks[-4]
        rsi = self.rsi(10)
        if direcao > 0 and rsi < 60: return 'CALL'
        if direcao < 0 and rsi > 40: return 'PUT'
        return 'SKIP'

class AlphaSmart(StrategyBase):
    def signal(self):
        if len(self.ticks) < 15: return 'SKIP'
        t = self.ticks
        up   = t[-1] > t[-2] > t[-3] > t[-4]
        down = t[-1] < t[-2] < t[-3] < t[-4]
        rsi  = self.rsi(7)
        if up   and rsi < 65: return 'CALL'
        if down and rsi > 35: return 'PUT'
        return 'SKIP'

class AlphaAnalytics(StrategyBase):
    def signal(self):
        if len(self.ticks) < 25: return 'SKIP'
        window = self.ticks[-20:]
        mean = sum(window) / len(window)
        std = math.sqrt(sum((x - mean)**2 for x in window) / len(window))
        if std == 0: return 'SKIP'
        zscore = (self.ticks[-1] - mean) / std
        if zscore < -1.5: return 'CALL'
        if zscore >  1.5: return 'PUT'
        return 'SKIP'

class AlphaSniper(StrategyBase):
    def signal(self):
        if len(self.ticks) < 50: return 'SKIP'
        cc = 0; cp = 0
        rsi = self.rsi(14); sma10 = self.sma(10); sma30 = self.sma(30)
        ema8 = self.ema(8); vol = self.volatility(10); avg = self.sma(10)
        vol_ok = (vol / avg) < 0.002 if avg else False
        if rsi < 40:              cc += 1
        if sma10 > sma30:         cc += 1
        if self.ticks[-1] > ema8: cc += 1
        if vol_ok:                cc += 1
        if rsi > 60:              cp += 1
        if sma10 < sma30:         cp += 1
        if self.ticks[-1] < ema8: cp += 1
        if vol_ok:                cp += 1
        if cc >= 4: return 'CALL'
        if cp >= 4: return 'PUT'
        return 'SKIP'

class MegaAlpha1(StrategyBase):
    def signal(self):
        if len(self.ticks) < 40: return 'SKIP'
        inputs = [
            (self.ema(5)  - self.ema(20)) / (self.ema(20) or 1),
            (self.rsi(14) - 50) / 50,
            (self.ticks[-1] - self.sma(10)) / (self.sma(10) or 1),
            self.volatility(10) / (self.sma(10) or 1),
        ]
        weights = [2.1, 1.8, 1.5, -0.9]
        score = sum(i * w for i, w in zip(inputs, weights))
        if score >  0.05: return 'CALL'
        if score < -0.05: return 'PUT'
        return 'SKIP'

class MegaAlpha2(StrategyBase):
    def __init__(self, ticks, win_rate=0.5):
        super().__init__(ticks)
        self.win_rate = win_rate
    def signal(self):
        if len(self.ticks) < 35: return 'SKIP'
        rsi = self.rsi(14); ema_s = self.ema(5); ema_l = self.ema(25)
        trend = (ema_s - ema_l) / (ema_l or 1)
        threshold = 0.001 if self.win_rate > 0.6 else 0.002
        if trend >  threshold and rsi < 60: return 'CALL'
        if trend < -threshold and rsi > 40: return 'PUT'
        return 'SKIP'

class MegaAlpha3(StrategyBase):
    def signal(self):
        if len(self.ticks) < 50: return 'SKIP'
        cp = 1 if self.ema(5) > self.ema(10) else -1
        mp = 1 if self.ema(10) > self.ema(20) else -1
        lp = 1 if self.ema(20) > self.ema(40) else -1
        rsi = self.rsi(14)
        score = cp + mp + lp
        if score ==  3 and rsi < 60: return 'CALL'
        if score == -3 and rsi > 40: return 'PUT'
        return 'SKIP'

class AlphaElite(StrategyBase):
    def signal(self):
        if len(self.ticks) < 20: return 'SKIP'
        moves = [1 if self.ticks[i] > self.ticks[i-1] else -1 for i in range(-7, 0)]
        run_up   = sum(1 for m in moves if m ==  1)
        run_down = sum(1 for m in moves if m == -1)
        rsi = self.rsi(7)
        if run_down >= 5 and rsi < 35: return 'CALL'
        if run_up   >= 5 and rsi > 65: return 'PUT'
        return 'SKIP'

class AlphaNexus(StrategyBase):
    def signal(self):
        if len(self.ticks) < 50: return 'SKIP'
        signals = [
            AlphaBot1(self.ticks).signal(),
            AlphaBot2(self.ticks).signal(),
            TitanCore(self.ticks).signal(),
            AlphaAnalytics(self.ticks).signal(),
            AlphaSniper(self.ticks).signal(),
        ]
        if signals.count('CALL') >= 3: return 'CALL'
        if signals.count('PUT')  >= 3: return 'PUT'
        return 'SKIP'

# ─────────────────────────────────────────────
# ESTRATÉGIAS — Dígitos (DIGITOVER/DIGITUNDER)
# ─────────────────────────────────────────────

class DigitStrategyBase(StrategyBase):
    """Base para estratégias de dígitos"""

    def _get_digit(self, price):
        return int(str(float(price)).replace('.', '')[-1])

    def _get_digits(self, n=100):
        prices = self.ticks[-n:] if len(self.ticks) >= n else self.ticks
        return [self._get_digit(p) for p in prices]

    def _freq(self, digits):
        c = Counter(digits)
        t = len(digits)
        return {d: c.get(d, 0) / t * 100 for d in range(10)}

    def _best_barrier(self, freq):
        best = None
        for barrier in range(1, 9):
            po = sum(freq.get(d, 0) for d in range(barrier + 1, 10))
            pu = sum(freq.get(d, 0) for d in range(0, barrier))
            direction = 'OVER' if po >= pu else 'UNDER'
            confidence = max(po, pu)
            if best is None or confidence > best[2]:
                best = (barrier, direction, confidence)
        return best  # (barrier, direction, confidence)

    def get_barrier(self):
        return getattr(self, '_last_barrier', 5)

    def signal(self) -> str:
        raise NotImplementedError


class AlphaBot4Digit(DigitStrategyBase):
    """Alpha Bot 4 FREE — frequência básica de dígitos"""
    def signal(self):
        if len(self.ticks) < 50: return 'SKIP'
        digits = self._get_digits(100)
        freq = self._freq(digits)
        barrier, direction, confidence = self._best_barrier(freq)
        self._last_barrier = barrier
        if confidence >= 60.0:
            return 'DIGITOVER' if direction == 'OVER' else 'DIGITUNDER'
        return 'SKIP'


class DigitSniper(DigitStrategyBase):
    """Digit Sniper VIP — entra contra o dígito mais quente"""
    def signal(self):
        if len(self.ticks) < 60: return 'SKIP'
        digits = self._get_digits(100)
        freq = self._freq(digits)
        hottest = max(freq, key=freq.get)
        coldest = min(freq, key=freq.get)
        if hottest >= 5:
            barrier = hottest - 1
            direction = 'UNDER'
            confidence = sum(freq.get(d, 0) for d in range(0, barrier))
        else:
            barrier = hottest + 1
            direction = 'OVER'
            confidence = sum(freq.get(d, 0) for d in range(barrier + 1, 10))
        cold_bonus = max(0, (10.0 - freq.get(coldest, 10)) * 0.5)
        confidence = min(confidence + cold_bonus, 95.0)
        self._last_barrier = barrier
        if confidence >= 62.0:
            return 'DIGITOVER' if direction == 'OVER' else 'DIGITUNDER'
        return 'SKIP'


class DigitPulse(DigitStrategyBase):
    """Digit Pulse VIP — detecta pulsos e entra na reversão"""
    def signal(self):
        if len(self.ticks) < 40: return 'SKIP'
        digits = self._get_digits(20)
        recent = digits[-8:]
        highs = sum(1 for d in recent if d > 4)
        lows  = len(recent) - highs
        if highs >= 6:
            self._last_barrier = 5
            confidence = 50 + (highs - 6) * 8.0
            if confidence >= 58: return 'DIGITUNDER'
        elif lows >= 6:
            self._last_barrier = 4
            confidence = 50 + (lows - 6) * 8.0
            if confidence >= 58: return 'DIGITOVER'
        return 'SKIP'


class MegaDigit1(DigitStrategyBase):
    """Mega Digit 1.0 PREMIUM — frequência + pulso + par/ímpar"""
    def signal(self):
        if len(self.ticks) < 70: return 'SKIP'
        digits = self._get_digits(100)
        freq = self._freq(digits)

        # 1. Frequência
        barrier, direction, freq_conf = self._best_barrier(freq)
        freq_score = (freq_conf - 50) * 0.8

        # 2. Pulso
        recent = digits[-10:]
        highs = sum(1 for d in recent if d > 4)
        lows  = len(recent) - highs
        if highs > lows:
            pulse_dir = 'UNDER'; pulse_score = (highs / 10 - 0.5) * 70
        else:
            pulse_dir = 'OVER';  pulse_score = (lows  / 10 - 0.5) * 70

        # 3. Par/Ímpar
        pi_conf = max(
            sum(1 for d in digits[-50:] if d % 2 == 0),
            sum(1 for d in digits[-50:] if d % 2 != 0)
        ) / 50 * 100
        pi_score = (pi_conf - 50) * 0.5

        total = min(50 + (freq_score * 0.40 + pulse_score * 0.35 + pi_score * 0.25), 95)

        # Direção: frequência ganha no empate
        final_dir = direction if direction == pulse_dir else direction
        self._last_barrier = barrier

        if total >= 65:
            return 'DIGITOVER' if final_dir == 'OVER' else 'DIGITUNDER'
        return 'SKIP'


class MegaDigit2(DigitStrategyBase):
    """Mega Digit 2.0 PREMIUM — janelas 25/50/100 com pesos"""
    def signal(self):
        if len(self.ticks) < 100: return 'SKIP'
        all_digits = self._get_digits(100)

        def analyze_window(digits, size):
            w = digits[-size:]
            if len(w) < size // 2: return None
            freq = self._freq(w)
            return self._best_barrier(freq)

        w25  = analyze_window(all_digits, 25)
        w50  = analyze_window(all_digits, 50)
        w100 = analyze_window(all_digits, 100)

        votes = {'OVER': 0.0, 'UNDER': 0.0}
        barrier_votes = {}
        for result, weight in [(w25, 0.50), (w50, 0.30), (w100, 0.20)]:
            if result:
                b, d, c = result
                votes[d] += weight * c
                barrier_votes[(b, d)] = barrier_votes.get((b, d), 0) + weight

        best_dir = max(votes, key=votes.get)
        total_weight = sum(w for r, w in [(w25,0.5),(w50,0.3),(w100,0.2)] if r)
        confidence = votes[best_dir] / total_weight if total_weight else 0

        best_b = max(
            ((b, d) for (b, d) in barrier_votes if d == best_dir),
            key=lambda x: barrier_votes[x],
            default=(5, best_dir)
        )[0]
        self._last_barrier = best_b

        if confidence >= 66:
            return 'DIGITOVER' if best_dir == 'OVER' else 'DIGITUNDER'
        return 'SKIP'


# ─────────────────────────────────────────────
# MAPA DE ESTRATÉGIAS
# ─────────────────────────────────────────────

STRATEGIES = {
    # Rise/Fall FREE
    'alpha_bot_1':     AlphaBot1,
    'alpha_bot_2':     AlphaBot2,
    'alpha_bot_3':     AlphaBot3,
    # Rise/Fall VIP
    'alpha_mind':      AlphaMind,
    'quantum_trader':  QuantumTrader,
    'titan_core':      TitanCore,
    'alpha_pulse':     AlphaPulse,
    'alpha_smart':     AlphaSmart,
    'alpha_analytics': AlphaAnalytics,
    'alpha_sniper':    AlphaSniper,
    # Rise/Fall PREMIUM
    'mega_alpha_1':    MegaAlpha1,
    'mega_alpha_2':    MegaAlpha2,
    'mega_alpha_3':    MegaAlpha3,
    'alpha_elite':     AlphaElite,
    'alpha_nexus':     AlphaNexus,
    # Dígitos FREE
    'alpha_bot_4':     AlphaBot4Digit,
    # Dígitos VIP
    'digit_sniper':    DigitSniper,
    'digit_pulse':     DigitPulse,
    # Dígitos PREMIUM
    'mega_digit_1':    MegaDigit1,
    'mega_digit_2':    MegaDigit2,
}

DIGIT_STRATEGIES = {'alpha_bot_4', 'digit_sniper', 'digit_pulse', 'mega_digit_1', 'mega_digit_2'}

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
        self.ticks     = []
        self.martingale_step = 0
        self.stake_atual     = config.get('stake_inicial', 1.0)

    def get_strategy(self):
        sid = self.config.get('strategy_id', 'alpha_bot_1')
        cls = STRATEGIES.get(sid, AlphaBot1)
        wr  = current_stats['win_rate'] / 100
        try:
            return cls(self.ticks, wr)
        except TypeError:
            return cls(self.ticks)

    def get_contract_type(self, signal):
        """
        Estratégias de dígitos já retornam DIGITOVER/DIGITUNDER.
        Estratégias Rise/Fall retornam CALL/PUT → converte conforme mercado.
        """
        sid = self.config.get('strategy_id', 'alpha_bot_1')
        if sid in DIGIT_STRATEGIES:
            return signal  # já é DIGITOVER ou DIGITUNDER

        symbol = self.config.get('symbol', 'R_100')
        if 'R_' in symbol or 'RDBEAR' in symbol or 'RDBULL' in symbol:
            if signal == 'CALL': return 'DIGITODD'
            if signal == 'PUT':  return 'DIGITEVEN'
        return signal

    def get_barrier(self):
        """Retorna barreira da estratégia de dígitos ativa, se houver"""
        sid = self.config.get('strategy_id', 'alpha_bot_1')
        if sid in DIGIT_STRATEGIES:
            strat = self.get_strategy()
            return getattr(strat, '_last_barrier', None)
        return None

    def calc_stake(self):
        risk = self.config.get('risk_mode', 'conservative')
        base = self.config.get('stake_inicial', 1.0)
        if risk == 'conservative':
            return base
        elif risk == 'balanced':
            return base * (1.5 ** self.martingale_step)
        else:
            return base * (2.0 ** self.martingale_step)

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
                    return True
            return False
        except Exception as e:
            print(f"❌ Erro conexão Deriv: {e}")
            return False

    async def subscribe_ticks(self):
        symbol = self.config.get('symbol', 'R_100')
        await self.ws.send(json.dumps({'ticks': symbol, 'subscribe': 1}))

    async def execute_trade_deriv(self, contract_type, stake):
        if not self.ws: return None
        try:
            proposal = {
                'proposal': 1, 'amount': stake, 'basis': 'stake',
                'contract_type': contract_type, 'currency': 'USD',
                'duration': 1, 'duration_unit': 't',
                'symbol': self.config['symbol']
            }
            # Adiciona barreira para contratos de dígitos
            barrier = self.get_barrier()
            if barrier is not None:
                proposal['barrier'] = barrier

            await self.ws.send(json.dumps(proposal))
            prop = json.loads(await self.ws.recv())
            if 'proposal' not in prop: return None
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
                if msg.get('msg_type') == 'tick':
                    price = float(msg['tick']['quote'])
                    self.ticks.append(price)
                    if len(self.ticks) > 200: self.ticks.pop(0)
                if len(self.ticks) >= 15:
                    strategy = self.get_strategy()
                    signal   = strategy.signal()
                    if signal != 'SKIP':
                        if current_stats['lucro_liquido'] >= self.config.get('lucro_alvo', 50):
                            current_stats['status_texto'] = '🎯 Lucro alvo atingido!'
                            self.running = False; break
                        if current_stats['lucro_liquido'] <= -self.config.get('limite_perda', 100):
                            current_stats['status_texto'] = '🛑 Limite de perda atingido!'
                            self.running = False; break
                        stake    = self.calc_stake()
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
                print(f"❌ Erro loop: {e}")
                await asyncio.sleep(3)
        if self.ws: await self.ws.close()

    def _run_simulation(self):
        price = 5000.0
        for _ in range(60):
            price += random.gauss(0, price * 0.001)
            self.ticks.append(round(price, 4))

        current_stats['status_texto'] = 'Buscando sinal...'
        wait_ticks = 0

        while self.running:
            price = self.ticks[-1] * (1 + random.gauss(0, 0.0008))
            self.ticks.append(round(price, 4))
            if len(self.ticks) > 200: self.ticks.pop(0)

            wait_ticks += 1
            if wait_ticks < 3:
                time.sleep(0.5)
                continue
            wait_ticks = 0

            if current_stats['lucro_liquido'] >= self.config.get('lucro_alvo', 50):
                current_stats['status_texto'] = '🎯 Lucro alvo atingido!'
                self.running = False; break
            if current_stats['lucro_liquido'] <= -self.config.get('limite_perda', 100):
                current_stats['status_texto'] = '🛑 Limite de perda atingido!'
                self.running = False; break

            strategy = self.get_strategy()
            signal   = strategy.signal()

            if signal != 'SKIP':
                stake    = self.calc_stake()
                contract = self.get_contract_type(signal)
                current_stats['status_texto'] = 'Contrato comprado'
                time.sleep(2)

                sid    = self.config.get('strategy_id', 'alpha_bot_1')
                wr_map = {
                    'alpha_bot_1': 0.72, 'alpha_bot_2': 0.74, 'alpha_bot_3': 0.71,
                    'alpha_mind': 0.78,  'quantum_trader': 0.80, 'titan_core': 0.79,
                    'alpha_pulse': 0.77, 'alpha_smart': 0.76, 'alpha_analytics': 0.78,
                    'alpha_sniper': 0.82, 'mega_alpha_1': 0.84, 'mega_alpha_2': 0.86,
                    'mega_alpha_3': 0.85, 'alpha_elite': 0.88, 'alpha_nexus': 0.87,
                    # Dígitos
                    'alpha_bot_4': 0.70, 'digit_sniper': 0.73, 'digit_pulse': 0.72,
                    'mega_digit_1': 0.75, 'mega_digit_2': 0.76,
                }
                won    = random.random() < wr_map.get(sid, 0.72)
                profit = stake * 0.95 if won else -stake
                self._update_stats(won, profit, contract, stake)
                if won: self.martingale_step = 0
                else:   self.martingale_step += 1
                current_stats['status_texto'] = 'Buscando sinal...'

            time.sleep(0.5)

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
        if len(trade_history) > 100: trade_history.pop()
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
    return jsonify({'status': 'ok', 'message': 'Alpha Dolar API Running',
                    'strategies': len(STRATEGIES), 'digit_strategies': len(DIGIT_STRATEGIES)})

@app.route('/api/bots/status')
def get_bots_status():
    return jsonify({k: {'running': v['running']} for k, v in bots_state.items()})

@app.route('/api/bot/start', methods=['POST'])
def start_bot():
    data     = request.json or {}
    bot_type = data.get('bot_type', 'ia_avancado')
    config   = data.get('config', {})
    global_config.update(config)
    if data.get('token'):      global_config['deriv_token']  = data['token']
    if data.get('account_type'): global_config['account_type'] = data['account_type']

    if bots_state[bot_type]['running']:
        return jsonify({'error': 'Bot já rodando'}), 400

    current_stats.update({
        'total_trades': 0, 'vitorias': 0, 'derrotas': 0,
        'lucro_liquido': 0.0, 'win_rate': 0.0, 'status_texto': 'Iniciando...'
    })

    bot = DerivBot(bot_type, global_config)
    if bot.start():
        bots_state[bot_type]['running']  = True
        bots_state[bot_type]['instance'] = bot
        return jsonify({'success': True, 'bot_type': bot_type,
                        'strategy': global_config.get('strategy_id'),
                        'is_digit': global_config.get('strategy_id') in DIGIT_STRATEGIES})

    return jsonify({'error': 'Falha ao iniciar'}), 500

@app.route('/api/bot/stop', methods=['POST'])
def stop_bot():
    for bt, state in bots_state.items():
        if state['running']:
            bot = state['instance']
            if bot: bot.stop()
            state['running'] = False
    current_stats['status_texto'] = 'Bot parado'
    return jsonify({'success': True, 'stats': current_stats})

@app.route('/api/bot/stats/ia')
def bot_stats_ia():
    any_running = any(s['running'] for s in bots_state.values())
    return jsonify({
        **current_stats,
        'running':  any_running,
        'balance':  current_stats['saldo_atual'],
        'strategy': global_config.get('strategy_id', 'alpha_bot_1'),
    })

@app.route('/api/bot/trades/ia')
def bot_trades_ia():
    limit = request.args.get('limit', 20, type=int)
    return jsonify(trade_history[:limit])

@app.route('/api/config', methods=['GET', 'POST'])
def config_route():
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
    port = int(os.environ.get('PORT', 10000))
    print("\n" + "="*60)
    print(f"🚀 ALPHA DOLAR 2.0 — {len(STRATEGIES)} estratégias carregadas")
    print(f"   Rise/Fall: 15 | Dígitos: {len(DIGIT_STRATEGIES)}")
    print("="*60 + "\n")
    app.run(host='0.0.0.0', port=port, debug=False)
