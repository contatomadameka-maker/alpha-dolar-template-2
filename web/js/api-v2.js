/**
 * API-V2.JS - Comunicação com Backend (Render)
 * FIXES 2026-02-27:
 *   ✅ Saldo buscado da API em tempo real (não mais do localStorage)
 *   ✅ Token real enviado corretamente no payload
 *   ✅ deriv_conta_ativa atualizado ao trocar de conta
 *   ✅ Símbolo enviado como código Deriv (R_100) não nome longo
 */

const API_BASE_URL = 'https://alpha-dolar-backend.onrender.com';

window.SystemState = {
    accountType: 'demo',
    bots: { ia: false, manual: false, auto: false },
    connected: false,
    balance: 0,
    profit: 0
};

// ==========================================
// HEALTH CHECK
// ==========================================

async function checkAPI() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/health`);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const data = await response.json();
        if (data.status === 'ok') {
            console.log('✅ API conectada:', data.message);
            window.SystemState.connected = true;
            updateConnectionStatus(true);
            return true;
        }
        throw new Error('API status not ok');
    } catch (error) {
        console.error('❌ Erro ao conectar API:', error);
        window.SystemState.connected = false;
        updateConnectionStatus(false);
        return false;
    }
}

function updateConnectionStatus(connected) {
    const el = document.getElementById('connectionStatus');
    if (el) {
        el.className = connected ? 'connection-status connected' : 'connection-status disconnected';
        el.title = connected ? 'Conectado ao servidor' : 'Desconectado';
    }
}

// ==========================================
// HELPER: pegar conta ativa do localStorage
// ==========================================

function getActiveAccount() {
    try {
        const accountType = localStorage.getItem('deriv_conta_ativa') || 'demo';
        const contas = JSON.parse(localStorage.getItem('deriv_accounts') || '[]');
        const isReal = accountType === 'real';
        const conta = contas.find(c => isReal ? c.isDemo === false : c.isDemo === true);
        return { accountType, conta, token: conta ? conta.token : null };
    } catch (e) {
        console.error('❌ Erro ao ler conta do localStorage:', e);
        return { accountType: 'demo', conta: null, token: null };
    }
}

// ==========================================
// VALIDAÇÃO DE SALDO (frontend)
// ==========================================

function validateConfigVsBalance(config, balance) {
    const stake    = parseFloat(config.initial_stake) || 0.35;
    const stopLoss = parseFloat(config.stop_loss)     || 5.0;
    const target   = parseFloat(config.target_profit) || 2.0;

    if (balance <= 0) {
        return { valid: false, message: '❌ Saldo indisponível ou não carregado. Aguarde e tente novamente.' };
    }
    if (stake > balance) {
        return { valid: false, message: `❌ Quantia inicial ($${stake.toFixed(2)}) é maior que seu saldo ($${balance.toFixed(2)}).\n\nRedua a quantia inicial para continuar.` };
    }
    if (stopLoss > balance) {
        return { valid: false, message: `❌ Limite de perda ($${stopLoss.toFixed(2)}) é maior que seu saldo ($${balance.toFixed(2)}).\n\nRedua o limite de perda para continuar.` };
    }
    if (stake * 10 > balance) {
        return { valid: true, warning: `⚠️ Saldo baixo para operação segura.\nRecomendamos pelo menos $${(stake * 10).toFixed(2)} para esta quantia inicial.\n\nDeseja continuar assim mesmo?`, requiresConfirm: true };
    }
    return { valid: true };
}

function showBalanceError(message) {
    if (typeof showNotification === 'function') { showNotification(message, 'error'); return; }
    if (typeof showToast === 'function')        { showToast(message, 'error'); return; }

    const existing = document.getElementById('_alphaBalanceError');
    if (existing) existing.remove();

    const toast = document.createElement('div');
    toast.id = '_alphaBalanceError';
    toast.style.cssText = `
        position: fixed; top: 24px; left: 50%; transform: translateX(-50%);
        background: #1a1a2e; border: 1px solid #f44336; border-radius: 12px;
        color: #fff; padding: 16px 24px; z-index: 99999;
        box-shadow: 0 8px 32px rgba(244,67,54,0.3);
        max-width: 380px; text-align: center; font-size: 14px; line-height: 1.5;
        white-space: pre-line;
    `;
    toast.innerHTML = `<span style="font-size:18px">⚠️</span><br>${message.replace(/^❌\s?/, '').replace(/^⚠️\s?/, '')}`;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 6000);
}

// ==========================================
// MAPA DE SÍMBOLOS (frontend)
// ==========================================

const SYMBOL_MAP = {
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
};

function resolveSymbol(s) {
    return SYMBOL_MAP[s] || s || 'R_100';
}

// ==========================================
// START BOT
// ==========================================

async function startBotAPI(botType, config) {
    try {
        console.log(`🚀 Iniciando bot tipo: ${botType}`, config);

        const { accountType, conta, token } = getActiveAccount();

        console.log(`📋 Conta ativa: ${accountType.toUpperCase()} | Token: ${token ? token.substring(0, 10) + '...' : 'NENHUM'}`);

        // Validação de saldo no frontend
        const currentBalance = window.SystemState.balance || 0;
        if (currentBalance > 0) {
            const validation = validateConfigVsBalance(config, currentBalance);
            if (!validation.valid) {
                showBalanceError(validation.message);
                throw new Error(validation.message);
            }
            if (validation.warning && validation.requiresConfirm) {
                const ok = window.confirm(validation.warning);
                if (!ok) throw new Error('Operação cancelada pelo usuário.');
            }
        }

        // ✅ Símbolo convertido para código Deriv
        const symbolCode = resolveSymbol(config.market || config.symbol || 'R_100');
        console.log(`📊 Símbolo: ${config.market} → ${symbolCode}`);

        const payload = {
            bot_type:     botType,
            account_type: accountType,
            token:        token,   // ✅ token real quando conta real
            config: {
                mode:          config.mode          || 'simples',
                symbol:        symbolCode,           // ✅ código correto (R_100)
                strategy:      config.strategy       || 'alpha_bot_balanced',
                trading_mode:  config.trading_mode   || 'fast',
                risk_mode:     config.risk_mode       || 'conservative',
                stake_inicial: parseFloat(config.initial_stake) || 0.35,
                lucro_alvo:    parseFloat(config.target_profit)  || 2,
                limite_perda:  parseFloat(config.stop_loss)      || 5,
                multiplicador: parseFloat(config.multiplier)     || 1,
                duracao:       parseInt(config.duration)         || 1
            }
        };

        console.log(`📤 Payload [${accountType.toUpperCase()}]:`, payload);

        const response = await fetch(`${API_BASE_URL}/api/bot/start`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const data = await response.json();

        if (!response.ok) {
            const errorMsg = data.error || `Erro HTTP ${response.status}`;
            showBalanceError(errorMsg);
            throw new Error(errorMsg);
        }

        console.log('✅ Robô iniciado:', data);
        window.SystemState.bots[botType] = true;
        return data;

    } catch (error) {
        console.error('❌ Erro ao iniciar robô:', error);
        throw error;
    }
}

// ==========================================
// STOP BOT
// ==========================================

async function stopBotAPI(botType) {
    try {
        console.log(`🛑 Parando bot tipo: ${botType}...`);

        const response = await fetch(`${API_BASE_URL}/api/bot/stop`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ bot_type: botType })
        });

        const data = await response.json();
        if (!response.ok) throw new Error(data.error || `HTTP ${response.status}`);

        console.log('✅ Robô parado:', data);
        window.SystemState.bots[botType] = false;
        return data;

    } catch (error) {
        console.error('❌ Erro ao parar robô:', error);
        throw error;
    }
}

// ==========================================
// GET STATS
// ==========================================

async function getStatsAPI(botType = 'ia') {
    try {
        const response = await fetch(`${API_BASE_URL}/api/bot/stats/${botType}`);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const data = await response.json();

        // ✅ Atualiza saldo do SystemState com valor real do bot
        if (data.stats && data.stats.balance !== undefined) {
            window.SystemState.balance = data.stats.balance;
            atualizarSaldoNaTela(data.stats.balance);
        }
        if (data.lucro_liquido  !== undefined) window.SystemState.profit  = data.lucro_liquido;
        if (data.bot_running    !== undefined) window.SystemState.bots[botType] = data.bot_running;
        if (data.running        !== undefined) window.SystemState.bots[botType] = data.running;

        return data;
    } catch (error) {
        console.error(`❌ Erro ao buscar stats (${botType}):`, error);
        throw error;
    }
}

// ==========================================
// GET BALANCE — ✅ busca saldo real da API
// ==========================================

async function getBalanceAPI() {
    try {
        const { accountType, conta } = getActiveAccount();

        // ✅ Tenta buscar saldo da API backend (bot conectado à Deriv)
        try {
            const response = await fetch(`${API_BASE_URL}/api/balance`);
            if (response.ok) {
                const data = await response.json();
                if (data.balance !== undefined && data.balance !== 9999) {
                    window.SystemState.balance = data.balance;
                    atualizarSaldoNaTela(data.balance);
                    return data;
                }
            }
        } catch (e) { /* fallback abaixo */ }

        // Fallback: usa saldo do localStorage se API não tem bot rodando
        if (conta && conta.balance !== undefined) {
            window.SystemState.balance = conta.balance;
            atualizarSaldoNaTela(conta.balance);
            return { balance: conta.balance };
        }

        return { balance: 0 };

    } catch (error) {
        console.error('❌ Erro ao buscar saldo:', error);
        throw error;
    }
}

// Função auxiliar para atualizar saldo na tela
function atualizarSaldoNaTela(balance) {
    const els = document.querySelectorAll(
        '.balance-value, #balanceValue, #saldoAtual, .saldo-valor, [data-balance]'
    );
    els.forEach(el => {
        el.textContent = `$${parseFloat(balance).toFixed(2)}`;
    });
}

// ==========================================
// GET HISTORY
// ==========================================

async function getHistoryAPI(botType = 'ia') {
    try {
        const response = await fetch(`${API_BASE_URL}/api/bot/history/${botType}`);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const data = await response.json();
        return data.history || [];
    } catch (error) {
        console.error('❌ Erro ao buscar histórico:', error);
        return [];
    }
}

// ==========================================
// SWITCH ACCOUNT TYPE
// ==========================================

function switchAccountType(type) {
    if (type !== 'demo' && type !== 'real') {
        console.error('❌ Tipo de conta inválido:', type);
        return;
    }

    const anyBotRunning = Object.values(window.SystemState.bots).some(r => r);
    if (anyBotRunning) {
        showBalanceError('Pare todos os robôs antes de trocar de conta!');
        return false;
    }

    window.SystemState.accountType = type;
    localStorage.setItem('accountType', type);
    localStorage.setItem('deriv_conta_ativa', type);  // ✅ atualiza conta ativa
    window.currentAccountType = type;

    updateAccountTypeUI(type);

    // ✅ Atualiza saldo da nova conta imediatamente do localStorage
    const { conta } = getActiveAccount();
    if (conta && conta.balance !== undefined) {
        window.SystemState.balance = conta.balance;
        atualizarSaldoNaTela(conta.balance);
        console.log(`💰 Saldo ${type.toUpperCase()}: $${conta.balance}`);
    }

    console.log(`🔄 Conta alterada para: ${type.toUpperCase()}`);
    return true;
}

function updateAccountTypeUI(type) {
    const demoBtn = document.getElementById('demoBtnSwitch');
    const realBtn = document.getElementById('realBtnSwitch');

    if (demoBtn && realBtn) {
        demoBtn.classList.toggle('active', type === 'demo');
        realBtn.classList.toggle('active', type === 'real');
    }

    const accountLabel = document.querySelector('.account-label');
    if (accountLabel) {
        accountLabel.textContent = type === 'demo' ? 'Conta Demo' : 'Conta Real';
        accountLabel.style.color = type === 'real' ? '#f44336' : '#4caf50';
    }
}

// ==========================================
// INITIALIZE
// ==========================================

document.addEventListener('DOMContentLoaded', async () => {
    console.log('🔌 Inicializando API...');

    const savedAccountType = localStorage.getItem('accountType') || 'demo';
    window.SystemState.accountType = savedAccountType;
    updateAccountTypeUI(savedAccountType);

    // ✅ Mostra saldo do localStorage imediatamente enquanto carrega
    const { conta } = getActiveAccount();
    if (conta && conta.balance !== undefined) {
        window.SystemState.balance = conta.balance;
        atualizarSaldoNaTela(conta.balance);
    }

    const connected = await checkAPI();

    if (connected) {
        console.log('✅ API inicializada!');
        try { await getBalanceAPI(); }
        catch (e) { console.warn('⚠️ Não foi possível buscar saldo inicial'); }
    } else {
        console.warn('⚠️ API não respondeu (pode estar dormindo)');
        console.log('💡 A primeira requisição pode demorar 50s...');
    }
});

console.log('✅ api-v2.js carregado!');