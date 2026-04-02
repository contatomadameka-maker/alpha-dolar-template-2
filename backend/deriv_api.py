"""
Conexão com Deriv API via WebSocket
Alpha Dolar 2.0 - VERSÃO ULTRA ESTÁVEL COM AUTO-COMPRA + TIMEOUT DE CONTRATO
"""
import json
import time
import websocket
from datetime import datetime
import threading

try:
    from .config import BotConfig
except ImportError:
    from config import BotConfig

class DerivAPI:
    def __init__(self, api_token=None):
        self.api_token  = api_token or BotConfig.API_TOKEN
        self.app_id     = BotConfig.APP_ID
        self.ws         = None
        self.is_connected  = False
        self.is_authorized = False
        self.account_info  = {}
        self.balance    = 0.0
        self.currency   = "USD"

        self.on_tick_callback     = None
        self.on_contract_callback = None
        self.on_balance_callback  = None

        self.should_reconnect = True
        self.ws_thread        = None
        self.keep_alive_thread = None
        self.last_message_time = time.time()

        # ✅ Controle de timeout de contrato (evita bot travar)
        self.current_contract_id  = None
        self.contract_timeout_sec = 30

    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        emoji = {"INFO":"ℹ️","SUCCESS":"✅","ERROR":"❌","WARNING":"⚠️","TRADE":"💰"}.get(level,"📝")
        print(f"[{timestamp}] {emoji} {message}")

    # ─── TIMEOUT DE CONTRATO ────────────────────────────────────────────────
    def _start_contract_timeout(self, contract_id):
        """Watchdog: se contrato não resolver em 30s, libera o bot"""
        self.current_contract_id = contract_id

        def _watchdog():
            time.sleep(self.contract_timeout_sec)
            if self.current_contract_id == contract_id:
                self.log(f"⏰ Timeout contrato {contract_id}! Liberando bot...", "WARNING")
                self.current_contract_id = None
                if self.on_contract_callback:
                    self.on_contract_callback({
                        "status": "lost", "profit": 0,
                        "contract_id": contract_id, "_timeout": True
                    })

        threading.Thread(target=_watchdog, daemon=True).start()

    def _clear_contract(self):
        self.current_contract_id = None

    # ─── KEEP-ALIVE ─────────────────────────────────────────────────────────
    def _keep_alive_loop(self):
        while self.should_reconnect and self.ws:
            try:
                if self.is_connected:
                    self._send({"ping": 1})
                    if time.time() - self.last_message_time > 30:
                        self.log("⚠️ Sem mensagens há 30s, reconectando...", "WARNING")
                        self._reconnect()
                time.sleep(5)
            except:
                pass

    # ─── CONEXÃO ────────────────────────────────────────────────────────────
    def connect(self):
        try:
            url = f"wss://ws.binaryws.com/websockets/v3?app_id={self.app_id}"
            self.log("Conectando à Deriv API...", "INFO")
            self.ws = websocket.WebSocketApp(
                url,
                on_open=self._on_open,
                on_message=self._on_message,
                on_error=self._on_error,
                on_close=self._on_close
            )
            self.ws_thread = threading.Thread(
                target=lambda: self.ws.run_forever(
                    ping_interval=0, ping_timeout=None, skip_utf8_validation=True
                ), daemon=True
            )
            self.ws_thread.start()

            start = time.time()
            while not self.is_connected and (time.time() - start) < 10:
                time.sleep(0.1)
            if not self.is_connected:
                raise Exception("Timeout na conexão")

            self.keep_alive_thread = threading.Thread(target=self._keep_alive_loop, daemon=True)
            self.keep_alive_thread.start()
            return True
        except Exception as e:
            self.log(f"Erro ao conectar: {e}", "ERROR")
            return False

    def _reconnect(self):
        try:
            self.log("🔄 Reconectando...", "INFO")
            if self.ws:
                try: self.ws.close()
                except: pass

            self.is_connected  = False
            self.is_authorized = False

            # ✅ Libera contrato preso ao reconectar
            if self.current_contract_id:
                self.log("⚠️ Contrato pendente liberado por reconexão", "WARNING")
                cid = self.current_contract_id
                self._clear_contract()
                if self.on_contract_callback:
                    self.on_contract_callback({
                        "status": "lost", "profit": 0,
                        "contract_id": cid, "_reconnect": True
                    })

            time.sleep(2)
            # Encerra threads antigas antes de reconectar
            if self.ws_thread and self.ws_thread.is_alive():
                self.ws_thread.join(timeout=3)
                self.ws_thread = None
            if self.keep_alive_thread and self.keep_alive_thread.is_alive():
                self.keep_alive_thread.join(timeout=3)
                self.keep_alive_thread = None
            if self.connect():
                if self.authorize():
                    self.log("✅ Reconexão bem-sucedida!", "SUCCESS")
                    if hasattr(self, '_subscribed_symbol'):
                        self.subscribe_ticks(self._subscribed_symbol)
        except Exception as e:
            self.log(f"Erro na reconexão: {e}", "ERROR")

    def disconnect(self):
        self.should_reconnect = False
        self.is_connected  = False
        self.is_authorized = False
        if self.ws:
            try: self.ws.close()
            except: pass
            self.ws = None
        # Aguarda threads encerrarem
        if self.ws_thread and self.ws_thread.is_alive():
            self.ws_thread.join(timeout=3)
            self.ws_thread = None
        if self.keep_alive_thread and self.keep_alive_thread.is_alive():
            self.keep_alive_thread.join(timeout=3)
            self.keep_alive_thread = None
        self.log("Desconectado da Deriv API", "INFO")

    def authorize(self):
        if not self.is_connected:
            self.log("Não conectado!", "ERROR")
            return False
        try:
            self.log("Autorizando...", "INFO")
            self._send({"authorize": self.api_token})
            start = time.time()
            while not self.is_authorized and (time.time() - start) < 15:
                time.sleep(0.1)
            if not self.is_authorized:
                raise Exception("Timeout na autorização")
            self.log(f"✅ Autorizado! Saldo: ${self.balance:.2f} {self.currency}", "SUCCESS")
            return True
        except Exception as e:
            self.log(f"Erro na autorização: {e}", "ERROR")
            return False

    def subscribe_ticks(self, symbol):
        self._subscribed_symbol = symbol
        self._send({"ticks": symbol, "subscribe": 1})
        self.log(f"Inscrito em ticks de {symbol}", "INFO")

    def subscribe_balance(self):
        self._send({"balance": 1, "subscribe": 1})

    def get_proposal(self, contract_type, symbol, amount, duration, duration_unit="t", barrier=None):
        proposal = {
            "proposal": 1,
            "amount": amount,
            "basis": BotConfig.BASIS,
            "contract_type": contract_type,
            "currency": self.currency,
            "duration": duration,
            "duration_unit": duration_unit,
            "symbol": symbol
        }
        if barrier is not None:
            proposal["barrier"] = str(barrier)
        self._send(proposal)
        self.log(f"Solicitando proposta: {contract_type} {symbol}", "INFO")

    def buy_contract(self, proposal_id, price):
        self._send({"buy": proposal_id, "price": price})
        self.log(f"Comprando contrato ID: {proposal_id}", "TRADE")

    def sell_contract(self, contract_id, price=0):
        self._send({"sell": contract_id, "price": price})

    def get_contract_info(self, contract_id):
        self._send({"proposal_open_contract": 1, "contract_id": contract_id, "subscribe": 1})

    def _send(self, data):
        if self.ws and self.is_connected:
            try:
                self.ws.send(json.dumps(data))
            except Exception as e:
                self.log(f"Erro ao enviar: {e}", "ERROR")
                self._reconnect()
        else:
            self.log("WebSocket não conectado!", "ERROR")

    # ─── CALLBACKS ──────────────────────────────────────────────────────────
    def _on_open(self, ws):
        self.is_connected      = True
        self.last_message_time = time.time()
        self.log("Conexão WebSocket aberta", "SUCCESS")

    def _on_message(self, ws, message):
        try:
            self.last_message_time = time.time()
            data     = json.loads(message)
            msg_type = data.get("msg_type")

            if msg_type == "ping":
                self._send({"pong": 1})

            elif msg_type == "authorize":
                if "error" in data:
                    self.log(f"Erro autorização: {data['error']['message']}", "ERROR")
                else:
                    self.is_authorized = True
                    auth = data.get("authorize", {})
                    self.account_info  = auth
                    self.balance  = float(auth.get("balance", 0))
                    self.currency = auth.get("currency", "USD")
                    self.subscribe_balance()

            elif msg_type == "balance":
                self.balance = float(data.get("balance", {}).get("balance", 0))
                if self.on_balance_callback:
                    self.on_balance_callback(self.balance)

            elif msg_type == "tick":
                if self.on_tick_callback:
                    self.on_tick_callback(data.get("tick", {}))

            elif msg_type == "proposal":
                if "error" in data:
                    self.log(f"Erro proposta: {data['error']['message']}", "ERROR")
                else:
                    proposal    = data.get("proposal", {})
                    proposal_id = proposal.get("id")
                    price       = proposal.get("ask_price")
                    self.log(f"Proposta recebida: ID {proposal_id}", "INFO")
                    if proposal_id and price:
                        self.log(f"🛒 Comprando automaticamente por ${price}", "TRADE")
                        self.buy_contract(proposal_id, price)

            elif msg_type == "buy":
                if "error" in data:
                    self.log(f"Erro compra: {data['error']['message']}", "ERROR")
                    # ✅ Libera waiting_contract em caso de erro na compra
                    self._clear_contract()
                    if self.on_contract_callback:
                        self.on_contract_callback({
                            "status": "lost", "profit": 0,
                            "contract_id": None, "_buy_error": True
                        })
                else:
                    buy_data    = data.get("buy", {})
                    contract_id = buy_data.get("contract_id")
                    self.log(f"✅ Compra realizada! ID: {contract_id}", "SUCCESS")
                    # ✅ Inicia timeout para este contrato
                    self._start_contract_timeout(contract_id)
                    self.get_contract_info(contract_id)

            elif msg_type == "proposal_open_contract":
                contract = data.get("proposal_open_contract", {})
                status   = contract.get("status")

                if self.on_contract_callback:
                    self.on_contract_callback(contract)

                if status in ["won", "lost"]:
                    profit = float(contract.get("profit", 0))
                    emoji  = "🎉 VITÓRIA" if status == "won" else "😞 DERROTA"
                    self.log(f"{emoji}! Lucro: ${profit:.2f}", "TRADE")
                    # ✅ Limpa timeout ao receber resultado
                    self._clear_contract()

            elif msg_type == "sell":
                if "error" in data:
                    self.log(f"Erro venda: {data['error']['message']}", "ERROR")
                else:
                    self.log(f"✅ Venda realizada!", "SUCCESS")

        except json.JSONDecodeError:
            self.log(f"Erro JSON: {message}", "ERROR")
        except Exception as e:
            self.log(f"Erro ao processar mensagem: {e}", "ERROR")

    def _on_error(self, ws, error):
        self.log(f"Erro WebSocket: {error}", "ERROR")

    def _on_close(self, ws, close_status_code, close_msg):
        self.is_connected  = False
        self.is_authorized = False
        self.log(f"Conexão fechada: {close_status_code} - {close_msg}", "WARNING")
        if self.should_reconnect:
            time.sleep(2)
            self._reconnect()

    def set_tick_callback(self, callback):
        self.on_tick_callback = callback

    def set_contract_callback(self, callback):
        self.on_contract_callback = callback

    def set_balance_callback(self, callback):
        self.on_balance_callback = callback