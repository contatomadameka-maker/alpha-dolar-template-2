/**
 * ALPHA DOLAR — FakeEngine v1.2
 * Config via aba admin separada usando localStorage como ponte
 */
(function() {
'use strict';

const urlParams = new URLSearchParams(window.location.search);
const SECRET_KEY = 'alpha2026';
const isAdmin = urlParams.get('key') === SECRET_KEY;

// Lê config do localStorage (ponte entre abas) ou URL
function lerConfig() {
  try {
    const saved = JSON.parse(localStorage.getItem('fe_config') || '{}');
    return {
      saldo_inicial: parseFloat(urlParams.get('saldo') || saved.saldo || 10000),
      velocidade:    parseFloat(urlParams.get('spd')   || saved.spd   || 1),
    };
  } catch(e) {
    return { saldo_inicial: 10000, velocidade: 1 };
  }
}

const cfg0 = lerConfig();

const CFG = {
  saldo_inicial:   cfg0.saldo_inicial,
  velocidade:      cfg0.velocidade,
  win_rate_alvo:   0.65,
  max_loss_streak: 7,
  max_win_streak:  7,
  tick_interval:   800,
  trade_duration:  3500,
  mercados: ['Volatility 10 Index','Volatility 25 Index','Volatility 50 Index','Volatility 75 Index','Volatility 100 Index']
};

const STATE = {
  running:false, saldo:CFG.saldo_inicial, saldo_inicial:CFG.saldo_inicial,
  total_trades:0, vitorias:0, derrotas:0, lucro_liquido:0,
  win_streak:0, loss_streak:0, stake_atual:0.35, stake_base:0.35,
  trades:[], forcando_win:false, timer_id:null, tick_id:null, preco_atual:1234.56,
  seq_index:0, pos_index:0,
  sequencias: [["L","L","W","L","W","W","L","W","W","L","W","L","W","L","W","W","W","L","W","L","W"],["L","W","L","L","W","L","W","L","W","W","L","W","W","L","W","W","L","W","L","W","W"],["W","L","W","W","L","W","L","W","L","L","W","W","L","W","W","L","W","L","W","W","L","W"],["L","L","W","W","L","W","L","L","L","W","W","W","L","W","L","W","W","L","W","W"],["W","L","W","W","L","W","L","L","W","W","L","W","L","W","L","W","W","L","W","W","L","W","L","W","W","L","W","W"],["W","W","L","W","L","W","L","L","W","W","L","W","W","L","W","L","W","W","L","W","W"],["W","L","L","W","W","L","W","L","W","L","W","L","L","W","W","L","W","W","L","W","L","W","L","W","W"],["W","L","W","W","L","L","W","L","W","L","W","W","L","W","L","L","W","W","L","W","W","L","W","L","W","W"],["L","W","W","L","W","L","L","W","L","W","L","W","W","L","W","W","L","W","L","L","W","W","L","W","W"],["W","L","L","W","L","W","W","L","W","L","W","L","W","W","L","W","W","L","W","L","W","W"],["L","W","W","L","W","L","W","W","L","L","W","W","L","W","L","W","L","W","W","L","W","W","L","W","W","L","W"],["L","W","W","L","L","W","L","W","W","L","W","W","L","L","W","W","L","W","W","L","W"],["L","W","L","W","W","L","W","L","L","W","W","L","W","W","L","W","W","W","L","W","L","W"],["L","L","W","L","L","W","W","L","W","W","L","W","W","L","W","L","W","W","L","W","W"],["W","L","W","L","W","L","L","W","W","L","W","W","L","W","L","L","W","W","L","W","W","L","W","L","W","W"],["W","W","L","W","L","L","L","W","L","W","W","L","W","W","L","L","W","W","W","L","W"],["W","L","W","L","W","L","W","W","L","L","W","L","W","W","L","W","W","L","W","W","L","W"],["W","L","W","L","L","L","L","W","W","L","W","W","L","W","L","W","W","L","W","W"],["L","L","W","W","L","W","W","L","L","W","L","W","W","L","W","L","W","W","L","W","L","W","W","L","W"],["L","W","W","L","W","L","L","W","W","L","W","W","L","W","L","W","W","L","W","W"],["L","W","W","L","L","L","W","W","L","W","L","L","W","W","W","L","W","W","L","W"],["L","W","L","W","W","L","W","L","L","W","W","L","W","W","L","W","L","W","W","L","W","L","W","W","L","W"],["W","W","L","L","L","W","L","W","W","L","W","L","L","L","W","W","W","L","W","W"],["L","L","L","W","L","W","W","L","W","W","L","W","L","W","W","L","W","W","L","W"],["L","W","L","W","W","L","L","W","W","L","W","L","W","L","W","W","L","L","W","W","L","W","W","L","W"],["W","L","W","L","L","W","W","L","W","W","L","W","L","L","W","W","L","W","W","L","W","L","W","W"],["L","W","L","W","L","W","W","L","W","L","L","W","W","L","W","L","W","W","L","W","L","W","W","L","W"],["W","L","W","W","L","L","W","L","W","W","L","W","L","W","W","L","W","L","W","W"],["W","W","L","L","W","L","W","L","W","W","L","L","W","W","L","W","L","W","L","W","W","L","W","W"],["L","W","L","L","W","W","L","W","L","W","W","L","W","W","L","W","L","W","W","L","W"]]
};

function injetarLoginFake() {
  // Lê saldo salvo — persiste entre sessoes
  const saldoSalvo = parseFloat(localStorage.getItem('fe_saldo_atual') || 0);
  const saldoUsar  = saldoSalvo > 0 ? saldoSalvo : CFG.saldo_inicial;
  STATE.saldo         = saldoUsar;
  STATE.saldo_inicial = saldoUsar;

  // ✅ ISOLAMENTO TOTAL — usa sessionStorage (só existe nessa aba)
  // SessionStorage é completamente separado do localStorage
  // Quando fechar a aba /live, some automaticamente
  // Nunca vaza para o dashboard real
  sessionStorage.setItem('deriv_accounts', JSON.stringify([{
    token:'FAKE_LIVE_TOKEN', acct:'VRTC000001',
    loginid:'VRTC000001', isDemo:true, currency:'USD', balance:saldoUsar
  }]));
  sessionStorage.setItem('deriv_conta_ativa', 'demo');

  // Saldo persistente fica so no fe_saldo_atual (chave unica nossa)
  localStorage.setItem('fe_saldo_atual', saldoUsar.toString());

  // ✅ Intercepta localStorage.getItem para /live usar sessionStorage
  // quando o dashboard pedir deriv_accounts
  const _getItemOrig = localStorage.getItem.bind(localStorage);
  const _setItemOrig = localStorage.setItem.bind(localStorage);

  localStorage.getItem = function(key) {
    // Redireciona chaves sensiveis para sessionStorage
    if (key === 'deriv_accounts' || key === 'deriv_conta_ativa') {
      return sessionStorage.getItem(key) || _getItemOrig(key);
    }
    return _getItemOrig(key);
  };

  localStorage.setItem = function(key, value) {
    // Intercepta tentativas de gravar conta fake no localStorage real
    if (key === 'deriv_accounts') {
      // So permite gravar se for conta real (tem token real)
      try {
        const contas = JSON.parse(value);
        const temFake = contas.some(c => c.token && c.token.includes('FAKE'));
        if (temFake) {
          sessionStorage.setItem(key, value);
          return;
        }
      } catch(e) {}
    }
    _setItemOrig(key, value);
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

// Atualiza display de lucro no topo (funciona para todos os modos)
function atualizarLucroTopo() {
  const lucro = STATE.lucro_liquido;
  const saldo = STATE.saldo;
  const pct   = STATE.saldo_inicial > 0 ? ((lucro / STATE.saldo_inicial) * 100).toFixed(2) : 0;
  const cor   = lucro >= 0 ? '#4caf50' : '#f44336';
  const sinal = lucro >= 0 ? '+' : '';

  // Tenta atualizar todos os displays de lucro/saldo do dashboard
  const lucroStr = `${sinal}$${Math.abs(lucro).toFixed(2)}`;
  const pctStr   = `(${sinal}${pct}%)`;

  // Display principal de lucro (topo esquerdo)
  const displays = [
    'botRunningProfit','lucroDisplay','profitDisplay',
    'lucroAcumuladoDisplay','totalProfitDisplay'
  ];
  displays.forEach(id => {
    const el = document.getElementById(id);
    if (el) { el.innerText = `${lucroStr} ${pctStr}`; el.style.color = cor; }
  });

  // Saldo no topo direito
  const saldoStr = '$' + saldo.toFixed(2);
  ['saldoDisplay','balanceDisplay','topBalanceDisplay','contaDemoValor','contaRealValor'].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.innerText = saldoStr;
  });
}

// Intercepta registrarTrade para garantir stake correto
function instalarInterceptorTrade() {
  const _orig = window.registrarTrade;
  if (!_orig || window._feInterceptado) return;
  window._feInterceptado = true;
  window.registrarTrade = function(p) {
    // Garante que valor e stake sejam os do FakeEngine
    if (p._fakeEngine) {
      return _orig(p);
    }
    // Bloqueia chamadas externas que nao sejam do FakeEngine
    return;
  };
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
  }

  // Calculo correto do Martingale para o dashboard
  const maxStep = CFG.max_loss_streak;
  const stepAtual = resultado === 'WIN' ? 0 : STATE.loss_streak;
  const proxStake = resultado === 'WIN' ? STATE.stake_base : STATE.stake_atual;

  const winRateAtual = STATE.total_trades > 0 ? parseFloat(((STATE.vitorias/STATE.total_trades)*100).toFixed(1)) : 0;

  const trade = {
    _fakeEngine: true, // marca para o interceptor
    // IDs
    id:          STATE.total_trades,
    trade_id:    STATE.total_trades,
    // Campos que o dashboard le
    tipo,
    mercado,
    valor:       stake,   // registrarTrade le como 'valor'
    stake:       stake,   // buscarTradesDoBackend le como 'stake'
    duracao:     '1 tick',
    resultado,
    lucro,
    profit:      lucro,   // alias
    // Martingale — dashboard usa snake_case
    proximoStake: proxStake,
    next_stake:   proxStake,
    proximo_stake:proxStake,
    step:         stepAtual,
    max_step:     CFG.max_loss_streak,  // dashboard le max_step
    max_steps:    CFG.max_loss_streak,  // alias
    maxStep:      CFG.max_loss_streak,  // camelCase tambem
    // Stats
    win_rate:    winRateAtual,
    winRate:     winRateAtual,
    total_trades:STATE.total_trades,
    totalTrades: STATE.total_trades,
    timestamp:   new Date().toISOString()
  };
  STATE.trades.unshift(trade);
  if (STATE.trades.length > 100) STATE.trades.pop();
  if (typeof window.registrarTrade === 'function') window.registrarTrade(trade);
  atualizarLucroTopo();

  // Força o dashboard a usar o stake correto do FakeEngine
  // Atualiza o input #initialStake para o proximo trade
  setTimeout(function() {
    const inputStake = document.getElementById('initialStake');
    if (inputStake) {
      inputStake.value = proxStake.toFixed(2);
      // Dispara evento de change para o dashboard detectar
      inputStake.dispatchEvent(new Event('input', {bubbles:true}));
      inputStake.dispatchEvent(new Event('change', {bubbles:true}));
    }
    // Atualiza também o display de stake no modal do bot rodando
    const displayStake = document.getElementById('botDisplayStake');
    if (displayStake) displayStake.innerText = '$' + proxStake.toFixed(2);
  }, 100);
  atualizarSaldoUI();
  STATE.timer_id = setTimeout(gerarTrade, (CFG.trade_duration + Math.random()*2500) / CFG.velocidade);
}

function atualizarSaldoUI() {
  const saldoStr = '$' + STATE.saldo.toFixed(2) + ' USD';
  ['balanceDisplay','saldoAtual','balance-value','demo-balance','proSaldoBox'].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.textContent = saldoStr;
  });
  document.querySelectorAll('[data-balance],.balance-amount,.saldo-valor').forEach(el => {
    el.textContent = saldoStr;
  });
  localStorage.setItem('deriv_balance_demo', STATE.saldo.toString());
  localStorage.setItem('fe_saldo_atual', STATE.saldo.toString()); // persiste entre sessoes
}

function iniciarTicks() {
  STATE.tick_id = setInterval(() => {
    STATE.preco_atual = parseFloat((STATE.preco_atual + (Math.random()-0.5)*0.5).toFixed(4));
    window.dispatchEvent(new CustomEvent('fakeTick',{detail:{
      symbol: window.selectedMarketSymbol||'R_100',
      quote: STATE.preco_atual, epoch: Math.floor(Date.now()/1000)
    }}));
  }, CFG.tick_interval / CFG.velocidade);
}

// Escuta mudanças do painel admin em outra aba
window.addEventListener('storage', function(e) {
  if (e.key === 'fe_config' && !isAdmin) {
    const cfg = JSON.parse(e.newValue || '{}');
    if (cfg.saldo !== undefined) {
      STATE.saldo = parseFloat(cfg.saldo);
      STATE.saldo_inicial = parseFloat(cfg.saldo);
      atualizarSaldoUI();
    }
    if (cfg.spd !== undefined) CFG.velocidade = parseFloat(cfg.spd);
  }
  // Comando start/stop da aba admin
  if (e.key === 'fe_cmd') {
    const cmd = JSON.parse(e.newValue || '{}');
    if (cmd.action === 'reload') window.location.reload();
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
      setTimeout(gerarTrade, 1500 / CFG.velocidade);
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
      }, CFG.tick_interval/CFG.velocidade);
    },
    _handle(msg) {
      if (msg.authorize) {
        this._respond({msg_type:'authorize',authorize:{loginid:'VRTC000001',balance:STATE.saldo,currency:'USD',fullname:'Alpha Trader'}});
      } else if (msg.balance) {
        this._respondBalance();
        setInterval(()=>{ if(this.readyState===1) this._respondBalance(); }, 3000/CFG.velocidade);
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
        }, CFG.trade_duration/CFG.velocidade);
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
  if (isAdmin) return; // Admin não precisa do badge
  const b=document.createElement('div');
  b.innerHTML='&#9679; LIVE';
  b.style.cssText='position:fixed;bottom:12px;right:12px;background:rgba(0,200,80,0.12);color:#00c850;border:1px solid rgba(0,200,80,0.25);border-radius:6px;padding:4px 10px;font-size:11px;font-family:monospace;z-index:99999;letter-spacing:1px;pointer-events:none;';
  document.body.appendChild(b);
}

// Painel admin — só aparece com ?key=alpha2026
function injetarPainelAdmin() {
  if (!isAdmin) return;

  // Página vira painel de controle dedicado
  document.body.innerHTML = '';
  document.body.style.cssText = 'background:#0d0f14;color:#fff;font-family:monospace;display:flex;align-items:center;justify-content:center;min-height:100vh;margin:0;';

  const painel = document.createElement('div');
  painel.style.cssText = 'background:#1a1d24;border:1px solid #2a2d35;border-radius:16px;padding:32px;min-width:340px;';
  painel.innerHTML = `
    <div style="text-align:center;margin-bottom:24px;">
      <div style="font-size:22px;font-weight:bold;color:#00c850;">⚙ FakeEngine Admin</div>
      <div style="font-size:12px;color:#555;margin-top:4px;">Configurações aplicadas em tempo real no /live</div>
    </div>

    <div style="margin-bottom:18px;">
      <div style="font-size:12px;color:#888;margin-bottom:6px;">💰 Saldo inicial</div>
      <div style="display:flex;gap:8px;">
        <input id="fe-saldo" type="number" value="${CFG.saldo_inicial}" style="flex:1;padding:8px 12px;background:#0d0f14;border:1px solid #333;color:#fff;border-radius:8px;font-size:14px;">
        <button onclick="aplicarSaldo()" style="padding:8px 16px;background:#00c850;border:none;color:#000;border-radius:8px;cursor:pointer;font-weight:bold;">Aplicar</button>
      </div>
      <div style="display:flex;gap:6px;margin-top:8px;">
        <button onclick="setSaldo(1000)"  style="flex:1;padding:5px;background:#1e2128;border:1px solid #333;color:#ccc;border-radius:6px;cursor:pointer;font-size:12px;">$1K</button>
        <button onclick="setSaldo(5000)"  style="flex:1;padding:5px;background:#1e2128;border:1px solid #333;color:#ccc;border-radius:6px;cursor:pointer;font-size:12px;">$5K</button>
        <button onclick="setSaldo(10000)" style="flex:1;padding:5px;background:#1e2128;border:1px solid #333;color:#ccc;border-radius:6px;cursor:pointer;font-size:12px;">$10K</button>
        <button onclick="setSaldo(50000)" style="flex:1;padding:5px;background:#1e2128;border:1px solid #333;color:#ccc;border-radius:6px;cursor:pointer;font-size:12px;">$50K</button>
      </div>
    </div>

    <div style="margin-bottom:18px;">
      <div style="font-size:12px;color:#888;margin-bottom:6px;">⚡ Velocidade das operações</div>
      <div style="display:flex;gap:8px;">
        <button id="spd-1" onclick="setSpd(1)" style="flex:1;padding:8px;background:#007bff;border:none;color:#fff;border-radius:8px;cursor:pointer;font-weight:bold;">1× Normal</button>
        <button id="spd-2" onclick="setSpd(2)" style="flex:1;padding:8px;background:#1e2128;border:1px solid #333;color:#ccc;border-radius:8px;cursor:pointer;">2× Rápido</button>
        <button id="spd-3" onclick="setSpd(3)" style="flex:1;padding:8px;background:#1e2128;border:1px solid #333;color:#ccc;border-radius:8px;cursor:pointer;">3× Turbo</button>
      </div>
    </div>

    <div style="margin-bottom:24px;">
      <div style="font-size:12px;color:#888;margin-bottom:6px;">🔗 URL para gravar</div>
      <div id="url-preview" style="padding:8px 12px;background:#0d0f14;border:1px solid #333;border-radius:8px;font-size:12px;color:#00c850;word-break:break-all;">alphadolar.online/live</div>
    </div>

    <button onclick="recarregarLive()" style="width:100%;padding:10px;background:#1e2128;border:1px solid #333;color:#888;border-radius:8px;cursor:pointer;font-size:12px;">
      🔄 Recarregar aba /live com novas configs
    </button>

    <div id="status-msg" style="text-align:center;margin-top:12px;font-size:12px;color:#555;"></div>
  `;
  document.body.appendChild(painel);

  let saldoAtual = CFG.saldo_inicial;
  let spdAtual   = CFG.velocidade;

  function salvarConfig() {
    localStorage.setItem('fe_config', JSON.stringify({saldo: saldoAtual, spd: spdAtual}));
    document.getElementById('url-preview').textContent = 'alphadolar.online/live?saldo='+saldoAtual+'&spd='+spdAtual;
    document.getElementById('status-msg').textContent = '✅ Config salva! Aba /live atualizada automaticamente.';
    setTimeout(()=>{ document.getElementById('status-msg').textContent=''; }, 3000);
  }

  window.setSaldo = function(v) {
    saldoAtual = v;
    document.getElementById('fe-saldo').value = v;
    salvarConfig();
  };
  window.aplicarSaldo = function() {
    saldoAtual = parseFloat(document.getElementById('fe-saldo').value) || 10000;
    salvarConfig();
  };
  window.setSpd = function(v) {
    spdAtual = v;
    [1,2,3].forEach(n => {
      const b = document.getElementById('spd-'+n);
      if(b) b.style.cssText = n===v
        ? 'flex:1;padding:8px;background:#007bff;border:none;color:#fff;border-radius:8px;cursor:pointer;font-weight:bold;'
        : 'flex:1;padding:8px;background:#1e2128;border:1px solid #333;color:#ccc;border-radius:8px;cursor:pointer;';
    });
    salvarConfig();
  };
  window.recarregarLive = function() {
    localStorage.setItem('fe_cmd', JSON.stringify({action:'reload', t:Date.now()}));
    document.getElementById('status-msg').textContent = '🔄 Comando enviado para aba /live...';
  };
}

window.FakeEngine = { getStats, getState:()=>STATE };

function init() {
  if (isAdmin) {
    injetarPainelAdmin();
    return;
  }
  injetarLoginFake();
  injetarBadge();
  // Instala interceptor — tenta agora e novamente após 1s (espera dashboard carregar)
  instalarInterceptorTrade();
  setTimeout(instalarInterceptorTrade, 500);
  setTimeout(instalarInterceptorTrade, 1500);
  setTimeout(instalarInterceptorTrade, 3000);
}

if (document.readyState==='loading') document.addEventListener('DOMContentLoaded',init);
else init();

})();
