/**
 * ALPHA DOLAR — FakeEngine v2.0
 * Config via aba admin: alphadolar.online/live?key=alpha2026
 */
(function() {
'use strict';

const urlParams = new URLSearchParams(window.location.search);
const SECRET_KEY = 'alpha2026';
const isAdmin = urlParams.get('key') === SECRET_KEY;

function lerConfig() {
  try {
    const saved = JSON.parse(localStorage.getItem('fe_config') || '{}');
    return {
      saldo_inicial: parseFloat(urlParams.get('saldo') || saved.saldo || 10000),
      spd_segundos:  parseFloat(saved.spd || urlParams.get('spd') || 15),
    };
  } catch(e) {
    return { saldo_inicial: 10000, spd_segundos: 15 };
  }
}

const cfg0 = lerConfig();

const CFG = {
  saldo_inicial:   cfg0.saldo_inicial,
  win_rate_alvo:   0.65,
  max_loss_streak: 7,
  tick_interval:   800,
  trade_duration:  cfg0.spd_segundos * 1000,
  mercados: ['Volatility 10 Index','Volatility 25 Index','Volatility 50 Index','Volatility 75 Index','Volatility 100 Index']
};

const STATE = {
  running:false, saldo:cfg0.saldo_inicial, saldo_inicial:cfg0.saldo_inicial,
  total_trades:0, vitorias:0, derrotas:0, lucro_liquido:0,
  win_streak:0, loss_streak:0, stake_atual:0.35, stake_base:0.35,
  trades:[], forcando_win:false, timer_id:null, tick_id:null, preco_atual:1234.56,
  seq_index:0, pos_index:0,
  sequencias: [["L","L","W","L","W","W","L","W","W","L","W","L","W","L","W","W","W","L","W","L","W"],["L","W","L","L","W","L","W","L","W","W","L","W","W","L","W","W","L","W","L","W","W"],["W","L","W","W","L","W","L","W","L","L","W","W","L","W","W","L","W","L","W","W","L","W"],["L","L","W","W","L","W","L","L","L","W","W","W","L","W","L","W","W","L","W","W"],["W","L","W","W","L","W","L","L","W","W","L","W","L","W","L","W","W","L","W","W","L","W","L","W","W","L","W","W"],["W","W","L","W","L","W","L","L","W","W","L","W","W","L","W","L","W","W","L","W","W"],["W","L","L","W","W","L","W","L","W","L","W","L","L","W","W","L","W","W","L","W","L","W","L","W","W"],["W","L","W","W","L","L","W","L","W","L","W","W","L","W","L","L","W","W","L","W","W","L","W","L","W","W"],["L","W","W","L","W","L","L","W","L","W","L","W","W","L","W","W","L","W","L","L","W","W","L","W","W"],["W","L","L","W","L","W","W","L","W","L","W","L","W","W","L","W","W","L","W","L","W","W"],["L","W","W","L","W","L","W","W","L","L","W","W","L","W","L","W","L","W","W","L","W","W","L","W","W","L","W"],["L","W","W","L","L","W","L","W","W","L","W","W","L","L","W","W","L","W","W","L","W"],["L","W","L","W","W","L","W","L","L","W","W","L","W","W","L","W","W","W","L","W","L","W"],["L","L","W","L","L","W","W","L","W","W","L","W","W","L","W","L","W","W","L","W","W"],["W","L","W","L","W","L","L","W","W","L","W","W","L","W","L","L","W","W","L","W","W","L","W","L","W","W"],["W","W","L","W","L","L","L","W","L","W","W","L","W","W","L","L","W","W","W","L","W"],["W","L","W","L","W","L","W","W","L","L","W","L","W","W","L","W","W","L","W","W","L","W"],["W","L","W","L","L","L","L","W","W","L","W","W","L","W","L","W","W","L","W","W"],["L","L","W","W","L","W","W","L","L","W","L","W","W","L","W","L","W","W","L","W","L","W","W","L","W"],["L","W","W","L","W","L","L","W","W","L","W","W","L","W","L","W","W","L","W","W"],["L","W","W","L","L","L","W","W","L","W","L","L","W","W","W","L","W","W","L","W"],["L","W","L","W","W","L","W","L","L","W","W","L","W","W","L","W","L","W","W","L","W","L","W","W","L","W"],["W","W","L","L","L","W","L","W","W","L","W","L","L","L","W","W","W","L","W","W"],["L","L","L","W","L","W","W","L","W","W","L","W","L","W","W","L","W","W","L","W"],["L","W","L","W","W","L","L","W","W","L","W","L","W","L","W","W","L","L","W","W","L","W","W","L","W"],["W","L","W","L","L","W","W","L","W","W","L","W","L","L","W","W","L","W","W","L","W","L","W","W"],["L","W","L","W","L","W","W","L","W","L","L","W","W","L","W","L","W","W","L","W","L","W","W","L","W"],["W","L","W","W","L","L","W","L","W","W","L","W","L","W","W","L","W","L","W","W"],["W","W","L","L","W","L","W","L","W","W","L","L","W","W","L","W","L","W","L","W","W","L","W","W"],["L","W","L","L","W","W","L","W","L","W","W","L","W","W","L","W","L","W","W","L","W"]]
};

function injetarLoginFake() {
  const saldoSalvo = parseFloat(localStorage.getItem('fe_saldo_atual') || 0);
  const saldoUsar  = saldoSalvo > 0 ? saldoSalvo : cfg0.saldo_inicial;
  STATE.saldo         = saldoUsar;
  STATE.saldo_inicial = saldoUsar;
  CFG.saldo_inicial   = saldoUsar;

  sessionStorage.setItem('deriv_accounts', JSON.stringify([{
    token:'FAKE_LIVE_TOKEN', acct:'VRTC000001',
    loginid:'VRTC000001', isDemo:true, currency:'USD', balance:saldoUsar
  }]));
  sessionStorage.setItem('deriv_conta_ativa', 'demo');
  localStorage.setItem('fe_saldo_atual', saldoUsar.toString());

  const _getOrig = localStorage.getItem.bind(localStorage);
  const _setOrig = localStorage.setItem.bind(localStorage);
  localStorage.getItem = function(key) {
    if (key === 'deriv_accounts' || key === 'deriv_conta_ativa') {
      return sessionStorage.getItem(key) || _getOrig(key);
    }
    return _getOrig(key);
  };
  localStorage.setItem = function(key, value) {
    if (key === 'deriv_accounts') {
      try {
        const contas = JSON.parse(value);
        if (contas.some(c => c.token && c.token.includes('FAKE'))) {
          sessionStorage.setItem(key, value);
          return;
        }
      } catch(e) {}
    }
    _setOrig(key, value);
  };
}

function decidirResultado(stake) {
  const lucro_sessao = STATE.saldo - STATE.saldo_inicial;
  if (lucro_sessao < -(STATE.saldo_inicial * 0.08)) STATE.forcando_win = true;
  if (STATE.forcando_win) { STATE.forcando_win = false; return 'WIN'; }
  if (STATE.loss_streak >= CFG.max_loss_streak) return 'WIN';
  const seq = STATE.sequencias[STATE.seq_index];
  const resultado = seq[STATE.pos_index] === 'W' ? 'WIN' : 'LOSS';
  STATE.pos_index++;
  if (STATE.pos_index >= seq.length) {
    STATE.pos_index = 0;
    STATE.seq_index = (STATE.seq_index + 1) % STATE.sequencias.length;
  }
  return resultado;
}

function calcularLucro(resultado, stake) {
  return resultado === 'WIN'
    ? parseFloat((stake * 0.87).toFixed(2))
    : parseFloat((-stake).toFixed(2));
}

function atualizarSaldoUI() {
  const saldoStr = '$' + STATE.saldo.toFixed(2) + ' USD';
  ['balanceDisplay','saldoAtual','balance-value','demo-balance'].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.textContent = saldoStr;
  });
  // proSaldoBox formato especial
  const proBox = document.getElementById('proSaldoBox');
  if (proBox) proBox.textContent = 'DEMO: $' + STATE.saldo.toFixed(2) + ' USD';
  document.querySelectorAll('[data-balance],.balance-amount,.saldo-valor').forEach(el => {
    el.textContent = saldoStr;
  });
  // NAO salva deriv_balance_demo para nao vazar para home real
  localStorage.setItem('fe_saldo_atual', STATE.saldo.toString());
}

function atualizarLucroTopo() {
  const lucro = STATE.lucro_liquido;
  const pct   = STATE.saldo_inicial > 0 ? ((lucro / STATE.saldo_inicial) * 100).toFixed(2) : 0;
  const cor   = lucro >= 0 ? '#4caf50' : '#f44336';
  const sinal = lucro >= 0 ? '+' : '';
  const lucroStr = sinal + '$' + Math.abs(lucro).toFixed(2);
  const pctStr   = '(' + sinal + pct + '%)';
  ['botRunningProfit','lucroDisplay','profitDisplay','lucroAcumuladoDisplay'].forEach(id => {
    const el = document.getElementById(id);
    if (el) { el.innerText = lucroStr + ' ' + pctStr; el.style.color = cor; }
  });
  const saldoStr = '$' + STATE.saldo.toFixed(2);
  ['saldoDisplay','balanceDisplay','topBalanceDisplay','contaDemoValor'].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.innerText = saldoStr;
  });
}

function gerarTrade() {
  if (!STATE.running) return;
  const stake     = STATE.stake_atual;
  const resultado = decidirResultado(stake);
  const lucro     = calcularLucro(resultado, stake);
  const mercado   = window.selectedMarketName || CFG.mercados[Math.floor(Math.random()*CFG.mercados.length)];
  const tipo      = Math.random() > 0.5 ? 'CALL' : 'PUT';

  STATE.total_trades++;
  STATE.saldo         = parseFloat((STATE.saldo + lucro).toFixed(2));
  STATE.lucro_liquido = parseFloat((STATE.lucro_liquido + lucro).toFixed(2));

  if (resultado === 'WIN') {
    STATE.vitorias++; STATE.win_streak++; STATE.loss_streak = 0;
    STATE.stake_atual = STATE.stake_base;
  } else {
    STATE.derrotas++; STATE.loss_streak++; STATE.win_streak = 0;
    STATE.stake_atual = parseFloat((STATE.stake_atual * 2.2).toFixed(2));
    if (STATE.stake_atual > STATE.stake_base * 128) STATE.stake_atual = STATE.stake_base;
    // Multi-estratégia fake: troca display após perda
    if (window._multiStrategyAtivo) {
      var estrategiasFake = ['Alpha Bot 1','Alpha Bot 2','Alpha Bot 3','Alpha Mind','Quantum Trader','Titan Core','Alpha Pulse','Alpha Smart','Mega Alpha 1.0','Alpha Elite','Alpha Nexus'];
      var atual = document.getElementById('botDisplayStrategy');
      if (atual) {
        var nomeAtual = atual.innerText.replace('⚡ ','');
        var opcoes = estrategiasFake.filter(function(e){ return e !== nomeAtual; });
        var nova = opcoes[Math.floor(Math.random() * opcoes.length)];
        atual.innerText = '⚡ ' + nova;
      }
    }
  }

  const winRateAtual = STATE.total_trades > 0 ? parseFloat(((STATE.vitorias/STATE.total_trades)*100).toFixed(1)) : 0;
  const maxStep = CFG.max_loss_streak;
  const stepAtual = resultado === 'WIN' ? 0 : STATE.loss_streak;
  const proxStake = resultado === 'WIN' ? STATE.stake_base : STATE.stake_atual;

  const trade = {
    _fakeEngine:true, id:STATE.total_trades, trade_id:STATE.total_trades,
    tipo, mercado, valor:stake, stake:stake, duracao:'1 tick',
    resultado, lucro, profit:lucro,
    proximoStake:proxStake, next_stake:proxStake, proximo_stake:proxStake,
    step:stepAtual, max_step:maxStep, max_steps:maxStep, maxStep,
    win_rate:winRateAtual, winRate:winRateAtual,
    total_trades:STATE.total_trades, totalTrades:STATE.total_trades,
    timestamp:new Date().toISOString()
  };

  STATE.trades.unshift(trade);
  if (STATE.trades.length > 100) STATE.trades.pop();
  if (typeof window.registrarTrade === 'function') window.registrarTrade(trade);

  setTimeout(function() {
    const inp = document.getElementById('initialStake');
    if (inp) {
      inp.value = proxStake.toFixed(2);
      inp.dispatchEvent(new Event('input', {bubbles:true}));
      inp.dispatchEvent(new Event('change', {bubbles:true}));
    }
    const disp = document.getElementById('botDisplayStake');
    if (disp) disp.innerText = '$' + STATE.stake_base.toFixed(2);
  }, 100);

  atualizarSaldoUI();
  atualizarLucroTopo();

  const baseMs = CFG.trade_duration;
  const varMs  = baseMs * 0.3;
  STATE.timer_id = setTimeout(gerarTrade, baseMs + (Math.random()*varMs*2 - varMs));
}

function iniciarTicks() {
  STATE.tick_id = setInterval(() => {
    STATE.preco_atual = parseFloat((STATE.preco_atual + (Math.random()-0.5)*0.5).toFixed(4));
    window.dispatchEvent(new CustomEvent('fakeTick',{detail:{
      symbol: window.selectedMarketSymbol||'R_100',
      quote: STATE.preco_atual, epoch: Math.floor(Date.now()/1000)
    }}));
  }, CFG.tick_interval);
}

function instalarInterceptorTrade() {
  const _orig = window.registrarTrade;
  if (!_orig || window._feInterceptado) return;
  window._feInterceptado = true;
  window.registrarTrade = function(p) {
    if (p._fakeEngine || p._manual) {
      if (p._manual) {
        const lucro = parseFloat(p.lucro || 0);
        STATE.lucro_liquido = parseFloat((STATE.lucro_liquido + lucro).toFixed(2));
        STATE.saldo         = parseFloat((STATE.saldo + lucro).toFixed(2));
        STATE.total_trades++;
        if (lucro > 0) STATE.vitorias++; else STATE.derrotas++;
        atualizarSaldoUI(); atualizarLucroTopo();
      }
      return _orig(p);
    }
  };
}

window.addEventListener('manualTradeRegistrado', function(e) {
  const lucro = parseFloat(e.detail.lucro || 0);
  STATE.lucro_liquido = parseFloat((STATE.lucro_liquido + lucro).toFixed(2));
  STATE.saldo         = parseFloat((STATE.saldo + lucro).toFixed(2));
  STATE.total_trades++;
  if (lucro > 0) STATE.vitorias++; else STATE.derrotas++;
  atualizarSaldoUI(); atualizarLucroTopo();
  localStorage.setItem('fe_saldo_atual', STATE.saldo.toString());
});

window.addEventListener('storage', function(e) {
  if (e.key === 'fe_config' && !isAdmin) {
    try {
      const cfg = JSON.parse(e.newValue || '{}');
      if (cfg.saldo !== undefined) {
        STATE.saldo = parseFloat(cfg.saldo);
        STATE.saldo_inicial = parseFloat(cfg.saldo);
        CFG.saldo_inicial = parseFloat(cfg.saldo);
        localStorage.setItem('fe_saldo_atual', cfg.saldo.toString());
        atualizarSaldoUI(); atualizarLucroTopo();
      }
      if (cfg.spd !== undefined) CFG.trade_duration = parseFloat(cfg.spd) * 1000;
    } catch(e2) {}
  }
  if (e.key === 'fe_cmd') {
    try {
      const cmd = JSON.parse(e.newValue || '{}');
      if (cmd.action === 'reload') window.location.reload();
    } catch(e2) {}
  }
});

const _fetchOrig = window.fetch;
window.fetch = async function(url, options) {
  const u = typeof url === 'string' ? url : url.toString();
  if (u.includes('alpha-dolar-backend') || u.includes('/api/bot')) {
    if (u.includes('/bot/start')) {
      const body = options && options.body ? JSON.parse(options.body) : {};
      STATE.stake_base  = body.config && body.config.stake_inicial ? body.config.stake_inicial : 0.35;
      STATE.stake_atual = STATE.stake_base;
      STATE.running = true;
      iniciarTicks();
      setTimeout(gerarTrade, 2000);
      return fakeResponse({success:true, bot_type:body.bot_type||'ia', strategy:'alpha_bot_1'});
    }
    if (u.includes('/bot/stop')) {
      STATE.running = false;
      clearTimeout(STATE.timer_id); clearInterval(STATE.tick_id);
      return fakeResponse({success:true, stats:getStats()});
    }
    if (u.includes('/bot/stats'))   return fakeResponse({...getStats(), success:true});
    if (u.includes('/bot/trades'))  return fakeResponse({success:true, trades:STATE.trades});
    if (u.includes('/bots/status')) return fakeResponse({ia:{running:STATE.running},ia_simples:{running:false},ia_avancado:{running:false},manual:{running:false}});
    if (u.includes('/health'))      return fakeResponse({status:'ok'});
    return fakeResponse({success:true});
  }
  return _fetchOrig.apply(this, arguments);
};

const _WSorig = window.WebSocket;
window.WebSocket = function(url) {
  if (url && url.includes('derivws.com')) return criarFakeWS(url);
  return new _WSorig(url);
};
window.WebSocket.CONNECTING=0; window.WebSocket.OPEN=1;
window.WebSocket.CLOSING=2;    window.WebSocket.CLOSED=3;

function criarFakeWS(url) {
  const ws = {
    url, readyState:1,
    onopen:null, onmessage:null, onerror:null, onclose:null,
    send(data) { try { setTimeout(()=>this._handle(JSON.parse(data)),50); } catch(e){} },
    close() { this.readyState=3; if(this.onclose) this.onclose({code:1000}); },
    _respond(data) { if(this.onmessage && this.readyState===1) this.onmessage({data:JSON.stringify(data)}); },
    _respondBalance() {
      this._respond({msg_type:'balance',balance:{balance:STATE.saldo,currency:'USD',loginid:'VRTC000001'}});
    },
    _startTicks(symbol) {
      const self=this;
      setInterval(()=>{
        if(self.readyState!==1) return;
        STATE.preco_atual=parseFloat((STATE.preco_atual+(Math.random()-0.5)*0.3).toFixed(4));
        self._respond({msg_type:'tick',tick:{symbol,quote:STATE.preco_atual,epoch:Math.floor(Date.now()/1000)}});
      }, CFG.tick_interval);
    },
    _handle(msg) {
      if (msg.authorize) {
        this._respond({msg_type:'authorize',authorize:{loginid:'VRTC000001',balance:STATE.saldo,currency:'USD',fullname:'Alpha Trader'}});
      } else if (msg.balance) {
        this._respondBalance();
        setInterval(()=>{ if(this.readyState===1) this._respondBalance(); }, 5000);
      } else if (msg.ticks) {
        this._startTicks(msg.ticks);
      } else if (msg.buy) {
        const cid='FAKE-'+Date.now(), stake=parseFloat(msg.price||0.35);
        this._respond({msg_type:'buy',buy:{contract_id:cid,payout:parseFloat((stake*1.87).toFixed(2)),buy_price:stake,transaction_id:Date.now()}});
        setTimeout(()=>{
          const res=decidirResultado(stake), luc=calcularLucro(res,stake);
          this._respond({msg_type:'proposal_open_contract',proposal_open_contract:{
            contract_id:cid, status:res==='WIN'?'won':'lost',
            profit:luc, sell_price:res==='WIN'?stake+luc:0,
            buy_price:stake, is_sold:1, is_expired:1, current_spot:STATE.preco_atual
          }});
        }, CFG.trade_duration);
      } else if (msg.proposal) {
        const stake=parseFloat(msg.amount||0.35);
        this._respond({msg_type:'proposal',proposal:{id:'PROP-'+Date.now(),ask_price:stake,payout:parseFloat((stake*1.87).toFixed(2)),spot:STATE.preco_atual,spot_time:Math.floor(Date.now()/1000)}});
      }
    }
  };
  setTimeout(()=>{ ws.readyState=1; if(ws.onopen) ws.onopen({type:'open'}); }, 100);
  return ws;
}

function fakeResponse(data, status=200) {
  return Promise.resolve(new Response(JSON.stringify(data),{status,headers:{'Content-Type':'application/json'}}));
}

function getStats() {
  const wr = STATE.total_trades > 0 ? parseFloat(((STATE.vitorias/STATE.total_trades)*100).toFixed(1)) : 0;
  return {running:STATE.running, total_trades:STATE.total_trades, vitorias:STATE.vitorias,
    derrotas:STATE.derrotas, lucro_liquido:STATE.lucro_liquido, win_rate:wr,
    saldo_atual:STATE.saldo, balance:STATE.saldo, status_texto:STATE.running?'Operando...':'Bot parado'};
}

function injetarBadge() {
  const b=document.createElement('div');
  b.innerHTML='&#9679; LIVE';
  b.style.cssText='position:fixed;bottom:12px;right:12px;background:rgba(0,200,80,0.12);color:#00c850;border:1px solid rgba(0,200,80,0.25);border-radius:6px;padding:4px 10px;font-size:11px;font-family:monospace;z-index:99999;letter-spacing:1px;pointer-events:none;';
  document.body.appendChild(b);
}

function injetarPainelAdmin() {
  if (!isAdmin) return;
  document.body.innerHTML = '';
  document.body.style.cssText = 'background:#0d0f14;color:#fff;font-family:monospace;display:flex;align-items:center;justify-content:center;min-height:100vh;margin:0;';

  const savedCfg = JSON.parse(localStorage.getItem('fe_config') || '{"saldo":10000,"spd":15}');
  const saldoInicial = savedCfg.saldo || 10000;
  const spdInicial   = savedCfg.spd   || 15;
  const spdMap = {5:1, 10:2, 15:3, 30:4, 45:5, 60:6};
  const spdIdAtivo = spdMap[spdInicial] || 3;

  const painel = document.createElement('div');
  painel.style.cssText = 'background:#1a1d24;border:1px solid #2a2d35;border-radius:16px;padding:32px;min-width:360px;max-width:420px;width:90%;';
  painel.innerHTML = `
    <div style="text-align:center;margin-bottom:24px;">
      <div style="font-size:22px;font-weight:bold;color:#00c850;">&#9881; FakeEngine Admin</div>
      <div style="font-size:12px;color:#555;margin-top:4px;">Configurações aplicadas em tempo real no /live</div>
    </div>
    <div style="margin-bottom:18px;">
      <div style="font-size:12px;color:#888;margin-bottom:6px;">&#128176; Saldo inicial</div>
      <div style="display:flex;gap:8px;">
        <input id="fe-saldo" type="number" value="${saldoInicial}" style="flex:1;padding:8px 12px;background:#0d0f14;border:1px solid #333;color:#fff;border-radius:8px;font-size:14px;">
        <button onclick="aplicarSaldo()" style="padding:8px 16px;background:#00c850;border:none;color:#000;border-radius:8px;cursor:pointer;font-weight:bold;">OK</button>
      </div>
      <div style="display:flex;gap:6px;margin-top:8px;">
        <button onclick="setSaldo(1000)"  style="flex:1;padding:5px;background:#1e2128;border:1px solid #333;color:#ccc;border-radius:6px;cursor:pointer;font-size:12px;">$1K</button>
        <button onclick="setSaldo(5000)"  style="flex:1;padding:5px;background:#1e2128;border:1px solid #333;color:#ccc;border-radius:6px;cursor:pointer;font-size:12px;">$5K</button>
        <button onclick="setSaldo(10000)" style="flex:1;padding:5px;background:#1e2128;border:1px solid #333;color:#ccc;border-radius:6px;cursor:pointer;font-size:12px;">$10K</button>
        <button onclick="setSaldo(50000)" style="flex:1;padding:5px;background:#1e2128;border:1px solid #333;color:#ccc;border-radius:6px;cursor:pointer;font-size:12px;">$50K</button>
      </div>
    </div>
    <div style="margin-bottom:18px;">
      <div style="font-size:12px;color:#888;margin-bottom:8px;">&#9201; Intervalo entre operações</div>
      <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;">
        <button id="spd-1" onclick="setSpd(1,5)"  style="padding:10px 4px;background:#1e2128;border:1px solid #333;color:#ccc;border-radius:8px;cursor:pointer;font-size:13px;">5s</button>
        <button id="spd-2" onclick="setSpd(2,10)" style="padding:10px 4px;background:#1e2128;border:1px solid #333;color:#ccc;border-radius:8px;cursor:pointer;font-size:13px;">10s</button>
        <button id="spd-3" onclick="setSpd(3,15)" style="padding:10px 4px;background:#1e2128;border:1px solid #333;color:#ccc;border-radius:8px;cursor:pointer;font-size:13px;">15s</button>
        <button id="spd-4" onclick="setSpd(4,30)" style="padding:10px 4px;background:#1e2128;border:1px solid #333;color:#ccc;border-radius:8px;cursor:pointer;font-size:13px;">30s</button>
        <button id="spd-5" onclick="setSpd(5,45)" style="padding:10px 4px;background:#1e2128;border:1px solid #333;color:#ccc;border-radius:8px;cursor:pointer;font-size:13px;">45s</button>
        <button id="spd-6" onclick="setSpd(6,60)" style="padding:10px 4px;background:#1e2128;border:1px solid #333;color:#ccc;border-radius:8px;cursor:pointer;font-size:13px;">60s</button>
      </div>
    </div>
    <div style="margin-bottom:18px;">
      <div style="font-size:12px;color:#888;margin-bottom:6px;">&#128279; URL para gravar</div>
      <div id="url-preview" style="padding:8px 12px;background:#0d0f14;border:1px solid #333;border-radius:8px;font-size:12px;color:#00c850;word-break:break-all;">alphadolar.online/live</div>
    </div>
    <button onclick="recarregarLive()" style="width:100%;padding:10px;background:#1e2128;border:1px solid #333;color:#888;border-radius:8px;cursor:pointer;font-size:12px;margin-bottom:8px;">
      &#128260; Recarregar aba /live com novas configs
    </button>
    <div id="status-msg" style="text-align:center;font-size:12px;color:#555;min-height:20px;"></div>
  `;
  document.body.appendChild(painel);

  setTimeout(()=>{
    const bAtivo = document.getElementById('spd-'+spdIdAtivo);
    if (bAtivo) { bAtivo.style.background='#007bff'; bAtivo.style.color='#fff'; bAtivo.style.border='none'; }
  }, 50);

  let saldoAtual = saldoInicial;
  let spdAtual   = spdInicial;

  function salvarConfig() {
    localStorage.setItem('fe_config', JSON.stringify({saldo: saldoAtual, spd: spdAtual}));
    document.getElementById('url-preview').textContent = 'alphadolar.online/live?saldo='+saldoAtual+'&spd='+spdAtual;
    const msg = document.getElementById('status-msg');
    if (msg) { msg.textContent = '\u2705 Salvo! Aba /live atualizada automaticamente.'; setTimeout(()=>{ msg.textContent=''; }, 3000); }
  }

  window.setSaldo = function(v) { saldoAtual=v; document.getElementById('fe-saldo').value=v; salvarConfig(); };
  window.aplicarSaldo = function() { saldoAtual=parseFloat(document.getElementById('fe-saldo').value)||10000; salvarConfig(); };

  window.setSpd = function(id, segundos) {
    spdAtual = segundos;
    [1,2,3,4,5,6].forEach(n => {
      const b = document.getElementById('spd-'+n);
      if (!b) return;
      b.style.background = n===id ? '#007bff' : '#1e2128';
      b.style.color      = n===id ? '#fff'    : '#ccc';
      b.style.border     = n===id ? 'none'    : '1px solid #333';
      b.style.fontWeight = n===id ? 'bold'    : 'normal';
    });
    salvarConfig();
  };

  window.recarregarLive = function() {
    localStorage.setItem('fe_cmd', JSON.stringify({action:'reload', t:Date.now()}));
    const msg = document.getElementById('status-msg');
    if (msg) msg.textContent = '&#128260; Comando enviado para aba /live...';
  };
}

window.FakeEngine = {
  getStats, getState: () => STATE,
  setCFG: function(obj) {
    if (obj.trade_duration !== undefined) CFG.trade_duration = obj.trade_duration;
    if (obj.saldo !== undefined) {
      STATE.saldo = obj.saldo; STATE.saldo_inicial = obj.saldo;
      atualizarSaldoUI(); atualizarLucroTopo();
    }
  }
};

function init() {
  if (isAdmin) { injetarPainelAdmin(); return; }
  injetarLoginFake();
  injetarBadge();
  setTimeout(instalarInterceptorTrade, 500);
  setTimeout(instalarInterceptorTrade, 1500);
  setTimeout(instalarInterceptorTrade, 3000);
}

if (document.readyState==='loading') document.addEventListener('DOMContentLoaded',init);
else init();

})();
