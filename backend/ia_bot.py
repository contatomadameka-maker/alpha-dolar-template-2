"""
ALPHA DOLAR 2.0 - Motor IA com Machine Learning
ia_bot.py — Bot separado, não interfere no bot.py existente

Arquitetura:
  - Coleta ticks em tempo real via DerivAPI existente
  - Extrai features (janela deslizante de dígitos)
  - Treina RandomForest online conforme coleta dados
  - Perdas virtuais antes de entrar real (DC Bot style)
  - Martingale configurável com multiplicador
  - Stop loss / Take profit integrados

Autor: Alpha Dolar 2.0
"""

import time
import threading
import numpy as np
from datetime import datetime
from collections import deque

try:
    from .deriv_api import DerivAPI
    from .config import BotConfig
except ImportError:
    from deriv_api import DerivAPI
    from config import BotConfig


# ═══════════════════════════════════════════
#  MOTOR ML ONLINE (sem arquivo externo)
# ═══════════════════════════════════════════

class MLMotorOnline:
    """
    RandomForest treinado online conforme coleta ticks.
    Fase 1 (< MIN_SAMPLES): só coleta, sem prever.
    Fase 2 (>= MIN_SAMPLES): treina e prevê.
    Retreina a cada RETRAIN_INTERVAL novas amostras.
    """
    MIN_SAMPLES      = 150   # amostras mínimas para primeiro treino
    RETRAIN_INTERVAL = 50    # retreina a cada N novas amostras
    WINDOW           = 20    # janela de dígitos para features
    CONFIDENCE_MIN   = 0.58  # confiança mínima para sinal válido

    def __init__(self):
        self.model        = None
        self.is_trained   = False
        self.accuracy     = 0.0
        self.X_buffer     = []   # features acumuladas
        self.y_buffer     = []   # labels acumuladas
        self._since_last  = 0    # amostras desde último treino
        self.digits       = deque(maxlen=500)  # histórico de dígitos

    def add_digit(self, d: int):
        """Adiciona dígito e gera amostra de treino se histórico suficiente."""
        self.digits.append(d)
        if len(self.digits) >= self.WINDOW + 1:
            features = self._make_features(list(self.digits)[-(self.WINDOW + 1):-1])
            label    = list(self.digits)[-1] % 2  # 0=ímpar, 1=par
            self.X_buffer.append(features)
            self.y_buffer.append(label)
            self._since_last += 1

        # Treina se atingiu mínimo ou intervalo de retreino
        if (not self.is_trained and len(self.X_buffer) >= self.MIN_SAMPLES) or \
           (self.is_trained and self._since_last >= self.RETRAIN_INTERVAL):
            self._treinar()

    def _make_features(self, window: list) -> list:
        """
        Features extraídas de uma janela de dígitos:
        - Os 20 dígitos brutos
        - Contagem de pares e ímpares
        - Razão par/(par+ímpar)
        - Comprimento da sequência atual (todos par ou todos ímpar)
        - Dígito mais frequente nos últimos 10
        - Desvio padrão
        """
        w = window[-self.WINDOW:]
        pares  = sum(1 for x in w if x % 2 == 0)
        impares = len(w) - pares
        ratio  = pares / len(w) if w else 0.5

        # sequência atual (streak)
        streak = 1
        for i in range(len(w) - 2, -1, -1):
            if (w[i] % 2) == (w[-1] % 2):
                streak += 1
            else:
                break

        # dígito mais frequente nos últimos 10
        last10    = w[-10:] if len(w) >= 10 else w
        freq_dig  = max(set(last10), key=last10.count) if last10 else 0
        std_val   = float(np.std(w)) if len(w) > 1 else 0.0

        features  = list(w) + [pares, impares, ratio, streak, freq_dig, std_val]
        return features

    def _treinar(self):
        """Treina (ou retreina) o RandomForest."""
        try:
            from sklearn.ensemble import RandomForestClassifier
            from sklearn.model_selection import train_test_split
            from sklearn.metrics import accuracy_score

            X = np.array(self.X_buffer)
            y = np.array(self.y_buffer)

            if len(set(y)) < 2:
                return  # precisa de ambas as classes

            X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=42)

            model = RandomForestClassifier(
                n_estimators=80,
                max_depth=8,
                random_state=42,
                n_jobs=-1,
                class_weight='balanced'
            )
            model.fit(X_tr, y_tr)

            self.accuracy = accuracy_score(y_te, model.predict(X_te))
            self.model    = model
            self.is_trained = True
            self._since_last = 0
            print(f"[IA ML] ✅ Modelo treinado | amostras={len(X)} | acurácia={self.accuracy:.2%}")

        except ImportError:
            print("[IA ML] ⚠️ scikit-learn não instalado! pip install scikit-learn")
        except Exception as e:
            print(f"[IA ML] ❌ Erro no treino: {e}")

    def predict(self, contract_type: str) -> tuple:
        """
        Retorna (deve_entrar: bool, confiança: float, descrição: str)
        contract_type: 'DIGITEVEN', 'DIGITODD', 'DIGITOVER', 'DIGITUNDER'
        """
        if not self.is_trained or len(self.digits) < self.WINDOW:
            # Fallback estatístico enquanto ML não está pronto
            return self._fallback_estatistico(contract_type)

        try:
            window   = list(self.digits)[-self.WINDOW:]
            features = self._make_features(window)
            X        = np.array([features])
            probas   = self.model.predict_proba(X)[0]

            # probas[0] = P(ímpar), probas[1] = P(par)
            p_par   = probas[1] if len(probas) > 1 else 0.5
            p_impar = probas[0]

            if contract_type == 'DIGITEVEN':
                conf    = p_par
                entrar  = conf >= self.CONFIDENCE_MIN
                desc    = f"ML P(par)={conf:.0%}"
            elif contract_type == 'DIGITODD':
                conf    = p_impar
                entrar  = conf >= self.CONFIDENCE_MIN
                desc    = f"ML P(ímpar)={conf:.0%}"
            elif contract_type == 'DIGITOVER':
                # Usa ratio dos últimos 10 como proxy
                last10 = list(self.digits)[-10:]
                altos  = sum(1 for d in last10 if d >= 5)
                conf   = altos / len(last10)
                entrar = conf < 0.40  # poucos altos → espera virada
                desc   = f"Stat altos={altos}/10"
            elif contract_type == 'DIGITUNDER':
                last10 = list(self.digits)[-10:]
                baixos = sum(1 for d in last10 if d <= 4)
                conf   = baixos / len(last10)
                entrar = conf < 0.40
                desc   = f"Stat baixos={baixos}/10"
            else:
                entrar, conf, desc = False, 0.0, "tipo desconhecido"

            return entrar, round(conf, 3), desc

        except Exception as e:
            print(f"[IA ML] Erro predict: {e}")
            return self._fallback_estatistico(contract_type)

    def _fallback_estatistico(self, contract_type: str) -> tuple:
        """Score estatístico simples enquanto ML aquece."""
        if len(self.digits) < 10:
            return False, 0.0, "coletando dados..."

        window = list(self.digits)[-20:] if len(self.digits) >= 20 else list(self.digits)
        pares  = sum(1 for d in window if d % 2 == 0)
        ratio  = pares / len(window)

        if contract_type == 'DIGITEVEN':
            conf   = ratio
            entrar = conf >= 0.60
            desc   = f"Stat par={ratio:.0%}"
        elif contract_type == 'DIGITODD':
            conf   = 1 - ratio
            entrar = conf >= 0.60
            desc   = f"Stat ímpar={1-ratio:.0%}"
        else:
            last10 = list(self.digits)[-10:]
            altos  = sum(1 for d in last10 if d >= 5)
            conf   = altos / 10
            entrar = conf < 0.40 if 'OVER' in contract_type else (1 - conf) < 0.40
            desc   = f"Stat fallback"

        return entrar, round(conf, 3), desc

    def get_info(self) -> dict:
        return {
            'treinado':    self.is_trained,
            'amostras':    len(self.X_buffer),
            'min_amostras': self.MIN_SAMPLES,
            'acuracia':    round(self.accuracy, 4),
            'digits_coletados': len(self.digits),
            'fase': 'ML ativo' if self.is_trained else f'Coletando ({len(self.X_buffer)}/{self.MIN_SAMPLES})',
        }


# ═══════════════════════════════════════════
#  BOT IA PRINCIPAL
# ═══════════════════════════════════════════

class IABot:
    """
    Motor IA separado do bot.py.
    Usa o mesmo DerivAPI e BotConfig existentes.
    """

    def __init__(self, config: dict = None):
        cfg = config or {}

        # Configurações recebidas do frontend
        self.symbol        = cfg.get('symbol', 'R_100')
        self.contract_type = cfg.get('contract_type', 'DIGITEVEN')
        self.stake_inicial = float(cfg.get('stake_inicial', 0.35))
        self.lucro_alvo    = float(cfg.get('lucro_alvo', 2.0))
        self.limite_perda  = float(cfg.get('limite_perda', 5.0))
        self.multiplicador = float(cfg.get('multiplicador', 2.2))
        self.perdas_virt   = int(cfg.get('perdas_virtuais', 3))
        self.neg_virt      = cfg.get('neg_virtuais', 'na_perda')   # na_perda | sempre | nunca
        self.iniciar_virt  = cfg.get('iniciar_com_virtuais', True)
        self.api_token     = cfg.get('token', BotConfig.API_TOKEN)

        # Motor ML
        self.ml = MLMotorOnline()

        # API Deriv (reutiliza o mesmo do projeto)
        self.api = DerivAPI(api_token=self.api_token)

        # Estado runtime
        self.is_running          = False
        self.waiting_contract    = False
        self.stake_atual         = self.stake_inicial
        self.perda_acumulada     = 0.0
        self.lucro_sessao        = 0.0
        self.virt_contador       = 0    # perdas virtuais acumuladas
        self.mart_step           = 0
        self._ultimo_stake_usado = self.stake_inicial
        self._ultimo_tick_time   = time.time()
        self._ultimo_trade_time  = time.time()
        self.stop_reason         = None
        self.stop_message        = None

        # Histórico de trades para o dashboard
        self.trades = []

        # Callback externo (chamado pelo api_production para registrar trades)
        self._on_trade_completed = None

    def log(self, msg, level="INFO"):
        ts    = datetime.now().strftime('%H:%M:%S')
        emoji = {"INFO":"ℹ️","SUCCESS":"✅","ERROR":"❌","WARNING":"⚠️",
                 "TRADE":"💰","WIN":"🎉","LOSS":"😞","ML":"🧠"}.get(level, "📝")
        print(f"[{ts}][IA] {emoji} {msg}")

    # ─── EXTRAI DÍGITO DO TICK ──────────────────────────────────────────────
    def _extrair_digito(self, quote: float) -> int:
        """Extrai último dígito da cotação."""
        try:
            s = f"{quote:.5f}".replace('.', '')
            return int(s[-1])
        except:
            return int(str(quote).replace('.', '')[-1]) if quote else 0

    # ─── CALLBACK TICK ──────────────────────────────────────────────────────
    def on_tick(self, tick_data: dict):
        self._ultimo_tick_time = time.time()

        if self.waiting_contract:
            return

        quote = float(tick_data.get('quote', 0))
        if not quote:
            return

        digito = self._extrair_digito(quote)
        self.ml.add_digit(digito)  # alimenta ML

        # Verifica se pode operar
        if not self.is_running:
            return

        if self.lucro_sessao >= self.lucro_alvo:
            self._parar('take_profit', f'Lucro alvo atingido: ${self.lucro_sessao:.2f}')
            return

        if self.perda_acumulada >= self.limite_perda:
            self._parar('stop_loss', f'Limite de perda atingido: ${self.perda_acumulada:.2f}')
            return

        # Pede sinal ao ML
        entrar, conf, desc = self.ml.predict(self.contract_type)

        if entrar:
            self._processar_sinal(digito, conf, desc)

    def _processar_sinal(self, digito: int, conf: float, desc: str):
        """Decide se entra virtual ou real."""

        # Modo: iniciar com virtuais
        if self.iniciar_virt and self.virt_contador < self.perdas_virt:
            self.virt_contador += 1
            self.log(f"🔮 VIRTUAL {self.virt_contador}/{self.perdas_virt} | {desc}", "ML")
            self._registrar_trade_virtual(digito)
            return

        # Modo neg_virt = 'na_perda': entra virtual apenas quando há perda acumulada
        if self.neg_virt == 'na_perda' and self.perda_acumulada > 0:
            if self.virt_contador < self.perdas_virt:
                self.virt_contador += 1
                self.log(f"🔮 VIRTUAL (recuperação) {self.virt_contador}/{self.perdas_virt}", "ML")
                self._registrar_trade_virtual(digito)
                return
            else:
                self.virt_contador = 0  # reset, entra real agora

        # Entra real
        self.log(f"🎯 SINAL REAL | conf={conf:.0%} | {desc} | stake=${self.stake_atual:.2f}", "TRADE")
        self._executar_trade()

    def _registrar_trade_virtual(self, digito: int):
        """Registra trade virtual no histórico (sem dinheiro real)."""
        trade = {
            'id':        int(time.time() * 1000),
            'tipo':      'virtual',
            'direction': self.contract_type,
            'result':    'virtual',
            'profit':    0.0,
            'stake':     self.stake_atual,
            'digito':    digito,
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'ml_fase':   self.ml.get_info()['fase'],
        }
        self.trades.append(trade)
        if len(self.trades) > 200:
            self.trades.pop(0)

    def _calcular_stake(self) -> float:
        """Calcula próximo stake com martingale de recuperação."""
        if self.perda_acumulada <= 0:
            return round(self.stake_inicial, 2)

        # Fórmula DC Bot: recupera perdas + lucro mínimo
        PAYOUT = 0.88
        stake  = (self.perda_acumulada + self.stake_inicial) / PAYOUT
        stake  = round(stake, 2)
        stake  = max(self.stake_inicial, stake)

        # Aplica multiplicador configurável
        if self.mart_step > 0:
            stake = round(self.stake_inicial * (self.multiplicador ** self.mart_step), 2)

        # Segurança: nunca mais que 70% do saldo
        if self.api.balance > 0:
            stake = min(stake, round(self.api.balance * 0.70, 2))

        return max(round(stake, 2), self.stake_inicial)

    def _executar_trade(self):
        """Envia proposta para a API Deriv."""
        stake = self._calcular_stake()

        if self.api.balance < stake:
            self.log(f"Saldo insuficiente! Necessário: ${stake:.2f}", "ERROR")
            self._parar('saldo_insuficiente', f'Saldo ${self.api.balance:.2f} < stake ${stake:.2f}')
            return

        self.stake_atual         = stake
        self._ultimo_stake_usado = stake
        self.waiting_contract    = True
        self._ultimo_trade_time  = time.time()

        barrier = None
        if self.contract_type == 'DIGITOVER':
            barrier = 4
        elif self.contract_type == 'DIGITUNDER':
            barrier = 5

        self.api.get_proposal(
            contract_type=self.contract_type,
            symbol=self.symbol,
            amount=stake,
            duration=1,
            duration_unit='t',
            barrier=barrier
        )

    # ─── CALLBACK CONTRATO ──────────────────────────────────────────────────
    def on_contract_update(self, contract_data: dict):
        status = contract_data.get('status')

        # Erros / timeout / reconexão
        if (contract_data.get('_timeout') or contract_data.get('_reconnect') or
                contract_data.get('_buy_error') or contract_data.get('_proposal_error')):
            self.log("⚠️ Operação interrompida — liberando para próximo sinal", "WARNING")
            self.waiting_contract = False
            self._ultimo_trade_time = time.time()
            return

        if status not in ['won', 'lost']:
            return

        sell_price = float(contract_data.get('sell_price', 0))
        buy_price  = float(contract_data.get('buy_price', 0))
        profit     = (sell_price - buy_price) if (sell_price > 0 or buy_price > 0) else float(contract_data.get('profit', 0))

        won       = status == 'won'
        exit_tick = contract_data.get('exit_tick_value') or contract_data.get('exit_tick')

        self.waiting_contract   = False
        self._ultimo_trade_time = time.time()

        if won:
            self.log(f"🎉 WIN! Lucro: ${profit:.2f}", "WIN")
            self.lucro_sessao    += abs(profit)
            self.perda_acumulada  = 0.0
            self.mart_step        = 0
            self.virt_contador    = 0
        else:
            self.log(f"😞 LOSS! Perda: ${abs(profit):.2f}", "LOSS")
            self.perda_acumulada += abs(profit)
            self.mart_step        = min(self.mart_step + 1, 6)

        # Registra trade
        trades_total = len(self.trades) + 1
        wins_total   = sum(1 for t in self.trades if t.get('result') == 'win') + (1 if won else 0)
        wr           = round((wins_total / trades_total) * 100, 1)

        trade = {
            'id':          int(time.time() * 1000),
            'tipo':        'real',
            'direction':   self.contract_type,
            'result':      'win' if won else 'loss',
            'profit':      round(profit, 2),
            'stake':       round(self._ultimo_stake_usado, 2),
            'next_stake':  round(self._calcular_stake(), 2),
            'mart_step':   self.mart_step,
            'perda_acum':  round(self.perda_acumulada, 2),
            'lucro_sessao': round(self.lucro_sessao, 2),
            'win_rate':    wr,
            'total_trades': trades_total,
            'exit_tick':   str(exit_tick) if exit_tick else None,
            'ml_fase':     self.ml.get_info()['fase'],
            'ml_acuracia': self.ml.get_info()['acuracia'],
            'timestamp':   datetime.now().strftime('%H:%M:%S'),
        }
        self.trades.append(trade)
        if len(self.trades) > 200:
            self.trades.pop(0)

        # Callback externo (registra no bots_state do api_production)
        if self._on_trade_completed:
            try:
                self._on_trade_completed(
                    self.contract_type, won, profit,
                    self._ultimo_stake_usado, self.symbol, exit_tick
                )
            except Exception as e:
                self.log(f"Erro callback: {e}", "WARNING")

        # Verifica stops após o trade
        if self.lucro_sessao >= self.lucro_alvo:
            self._parar('take_profit', f'Lucro alvo atingido: ${self.lucro_sessao:.2f}')
        elif self.perda_acumulada >= self.limite_perda:
            self._parar('stop_loss', f'Limite de perda atingido: ${self.perda_acumulada:.2f}')

    def on_balance_update(self, balance: float):
        self.log(f"💰 Saldo: ${balance:.2f}", "INFO")

    # ─── START / STOP ────────────────────────────────────────────────────────
    def start(self):
        self.log("Conectando à Deriv API...", "INFO")
        if not self.api.connect():
            self.log("Falha na conexão!", "ERROR")
            return False

        if not self.api.authorize():
            self.log("Falha na autorização!", "ERROR")
            return False

        self.log(f"✅ Autorizado! Saldo: ${self.api.balance:.2f}", "SUCCESS")
        self.log(f"🧠 Motor ML iniciado — coletando {self.ml.MIN_SAMPLES} amostras para treinar", "ML")
        self.log(f"🎯 Contrato: {self.contract_type} | Mercado: {self.symbol}", "INFO")
        self.log(f"🔮 Perdas virtuais: {self.perdas_virt} | Mult: {self.multiplicador}×", "INFO")

        self.api.set_tick_callback(self.on_tick)
        self.api.set_contract_callback(self.on_contract_update)
        self.api.set_balance_callback(self.on_balance_update)
        self.api.subscribe_ticks(self.symbol)
        self.api._bot_ref = self

        self.is_running = True

        WATCHDOG_CONTRATO = 45
        TICK_TIMEOUT      = 15

        while self.is_running:
            time.sleep(1)
            agora = time.time()

            # Watchdog contrato preso
            if self.waiting_contract:
                if agora - self._ultimo_trade_time > WATCHDOG_CONTRATO:
                    self.log("⏰ WATCHDOG: contrato preso — liberando!", "WARNING")
                    self.waiting_contract   = False
                    self._ultimo_trade_time = agora
                continue

            # Watchdog sem ticks
            if agora - self._ultimo_tick_time > TICK_TIMEOUT:
                self.log("⚠️ WATCHDOG: sem ticks — reconectando...", "WARNING")
                try:
                    self.api.subscribe_ticks(self.symbol)
                    self._ultimo_tick_time = agora
                except Exception as e:
                    self.log(f"Erro re-subscrever: {e}", "ERROR")

        return True

    def stop(self):
        self.is_running = False
        if self.api:
            self.api.disconnect()
        self.log("Bot IA encerrado.", "INFO")

    def _parar(self, motivo: str, mensagem: str):
        self.log(f"🛑 {mensagem}", "WARNING")
        self.stop_reason  = motivo
        self.stop_message = mensagem
        self.is_running   = False

    # ─── STATS PARA O DASHBOARD ─────────────────────────────────────────────
    def get_stats(self) -> dict:
        total  = len([t for t in self.trades if t.get('tipo') == 'real'])
        wins   = sum(1 for t in self.trades if t.get('tipo') == 'real' and t.get('result') == 'win')
        wr     = round((wins / total * 100), 1) if total > 0 else 0
        return {
            'total_trades':   total,
            'vitorias':       wins,
            'derrotas':       total - wins,
            'win_rate':       wr,
            'lucro_sessao':   round(self.lucro_sessao, 2),
            'perda_acumulada': round(self.perda_acumulada, 2),
            'saldo_liquido':  round(self.lucro_sessao - self.perda_acumulada, 2),
            'balance':        self.api.balance if self.api else 0,
            'currency':       self.api.currency if self.api else 'USD',
            'mart_step':      self.mart_step,
            'stake_atual':    round(self.stake_atual, 2),
            'virt_contador':  self.virt_contador,
            'perdas_virt':    self.perdas_virt,
            'ml':             self.ml.get_info(),
        }