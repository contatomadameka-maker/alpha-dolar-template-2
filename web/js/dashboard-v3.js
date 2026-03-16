/**
 * DASHBOARD-V3.JS - VERSÃO CORRIGIDA
 * Sistema DEMO/REAL + Integração com trading.html
 * Alpha Dolar 2.0
 *
 * ✅ USA window.API_BASE_URL corretamente
 * ✅ USA modal correto: botRunningModal
 */

// ==========================================
// ✅ USA O QUE JÁ EXISTE
// ==========================================
// ✅ GARANTIR QUE API_BASE_URL EXISTE

console.log('✅ dashboard-v3.js carregado! API:', window.API_BASE_URL);

// ==========================================
// SISTEMA DEMO/REAL
// ==========================================

let currentAccountMode = 'demo';
let balanceUpdateInterval = null;

async function initAccountMode() {
    console.log('🔑 Inicializando sistema DEMO/REAL...');

    try {
        const response = await fetch(`${window.API_BASE_URL}/api/account/mode`);
        const data = await response.json();

        if (data.success) {
            currentAccountMode = data.mode;
            updateAccountModeUI(data.mode);
            await updateBalance();
            startBalanceAutoUpdate();
            console.log(`✅ Modo: ${data.mode.toUpperCase()}`);
        }
    } catch (error) {
        console.error('❌ Erro ao carregar modo:', error);
        updateAccountModeUI('demo');
    }
}

function updateAccountModeUI(mode) {
    const demoBtn = document.getElementById('demo-btn');
    const realBtn = document.getElementById('real-btn');

    if (demoBtn && realBtn) {
        demoBtn.classList.remove('active');
        realBtn.classList.remove('active');

        if (mode === 'demo') {
            demoBtn.classList.add('active');
        } else {
            realBtn.classList.add('active');
        }
    }

    currentAccountMode = mode;

    const labels = document.querySelectorAll('.account-mode-label, #mobile-mode-label');
    labels.forEach(label => {
        const text = mode === 'demo' ? 'Conta Demo' : 'Conta Real';
        label.textContent = text;
        label.className = 'account-mode-label ' + mode;
    });
}

async function switchAccountMode(newMode) {
    if (currentAccountMode === newMode) {
        console.log(`ℹ️ Já em modo ${newMode.toUpperCase()}`);
        return;
    }

    if (newMode === 'real') {
        const confirmed = confirm(
            '⚠️ ATENÇÃO!\n\n' +
            'Você mudará para CONTA REAL.\n' +
            'Operações usarão DINHEIRO REAL!\n\n' +
            'Todos os bots serão parados.\n\n' +
            'Continuar?'
        );

        if (!confirmed) {
            console.log('❌ Cancelado');
            return;
        }
    }

    try {
        const response = await fetch(`${window.API_BASE_URL}/api/account/mode`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ mode: newMode })
        });

        const data = await response.json();

        if (data.success) {
            updateAccountModeUI(newMode);
            await updateBalance();

            const emoji = newMode === 'demo' ? '🎮' : '💰';
            alert(`${emoji} Modo: ${newMode.toUpperCase()}!`);

            if (data.stopped_bots && data.stopped_bots.length > 0) {
                setTimeout(() => {
                    alert(`🛑 ${data.stopped_bots.length} bot(s) parado(s)`);
                }, 1000);
            }

            if (window.SystemState && window.SystemState.bots) {
                for (let botType in window.SystemState.bots) {
                    window.SystemState.bots[botType] = false;
                }
            }

            if (window.statsPollingInterval) {
                clearInterval(window.statsPollingInterval);
                window.statsPollingInterval = null;
            }

            console.log(`✅ Modo: ${newMode.toUpperCase()}`);
        } else {
            alert(`❌ ${data.error}`);
            console.error('❌', data.error);
        }
    } catch (error) {
        console.error('❌ Erro:', error);
        alert('❌ Erro ao mudar modo');
    }
}

async function updateBalance() {
    try {
        const response = await fetch(`${window.API_BASE_URL}/api/account/balance`);
        const data = await response.json();

        if (data.success) {
            const balanceEl = document.getElementById('account-balance');
            if (balanceEl) {
                balanceEl.textContent = data.formatted;
                balanceEl.classList.add('balance-update');
                setTimeout(() => balanceEl.classList.remove('balance-update'), 300);
            }

            const mobileEl = document.getElementById('mobileBalance');
            if (mobileEl) {
                mobileEl.textContent = data.formatted;
            }

            const statEl = document.getElementById('statBalance');
            if (statEl) {
                statEl.textContent = `$${data.balance.toFixed(0)}`;
            }

            const key = `${data.mode}_${data.balance}`;
            if (window.lastBalanceKey !== key) {
                console.log(`💰 Saldo: ${data.formatted} (${data.mode.toUpperCase()})`);
                window.lastBalanceKey = key;
            }
        }
    } catch (error) {
        console.error('❌ Erro ao atualizar saldo:', error);
    }
}

function startBalanceAutoUpdate() {
    if (balanceUpdateInterval) {
        clearInterval(balanceUpdateInterval);
    }

    balanceUpdateInterval = setInterval(() => {
        updateBalance();
    }, 10000);

    console.log('✅ Auto-update saldo (10s)');
}

function stopBalanceAutoUpdate() {
    if (balanceUpdateInterval) {
        clearInterval(balanceUpdateInterval);
        balanceUpdateInterval = null;
        console.log('🛑 Auto-update parado');
    }
}

function setupAccountModeListeners() {
    const demoBtn = document.getElementById('demo-btn');
    const realBtn = document.getElementById('real-btn');

    if (demoBtn) {
        demoBtn.addEventListener('click', () => {
            console.log('🎮 DEMO clicado');
            switchAccountMode('demo');
        });
    }

    if (realBtn) {
        realBtn.addEventListener('click', () => {
            console.log('💰 REAL clicado');
            switchAccountMode('real');
        });
    }

    console.log('✅ Listeners DEMO/REAL configurados');
}

// ==========================================
// ✅ INTEGRAÇÃO COM TRADING.HTML - CORRIGIDA
// ==========================================

function setupTradingButton() {
    // ✅ DESABILITADO - O botão é configurado pelo trading.html
    console.log('⚠️ setupTradingButton() desabilitado (botão configurado pelo trading.html)');
    return;

    const startBtn = document.getElementById('startButton');

    if (startBtn && !startBtn.hasAttribute('data-event-added')) {
        console.log('🔘 Configurando botão startButton...');

        startBtn.onclick = async function() {
            console.log('🎯 Botão startButton clicado!');

            const botType = 'ia';
            const isRunning = window.botRunning || false;

            if (isRunning) {
                console.log('🛑 Parando bot...');

                try {
                    startBtn.disabled = true;
                    startBtn.textContent = 'Parando...';

                    const response = await fetch(`${window.API_BASE_URL}/api/bot/stop`, {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({bot_type: botType})
                    });

                    const result = await response.json();

                    console.log('✅ Bot parado!', result);

                    startBtn.textContent = 'Iniciar Bot';
                    startBtn.classList.remove('running');
                    window.botRunning = false;

                    // ✅ USA MODAL CORRETO: botRunningModal
                    const modal = document.getElementById('botRunningModal');
                    if (modal) {
                        modal.classList.remove('active');
                        console.log('📂 Modal botRunningModal fechado');
                    }

                } catch (error) {
                    console.error('❌ Erro ao parar:', error);
                } finally {
                    startBtn.disabled = false;
                }

            } else {
                console.log('🚀 Iniciando bot...');

                const config = {
                    mode: 'simples',
                    market: 'R_100',
                    strategy: 'alpha_bot_1',
                    trading_mode: 'fast',
                    risk_mode: 'conservative',
                    initial_stake: 0.35,
                    target_profit: 2,
                    stop_loss: 5,
                    multiplier: 1,
                    duration: 1
                };

                try {
                    startBtn.disabled = true;
                    startBtn.textContent = 'Iniciando...';

                    const response = await fetch(`${window.API_BASE_URL}/api/bot/start`, {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({bot_type: botType, config: config})
                    });

                    const result = await response.json();

                    if (result.success) {
                        console.log('✅ Bot iniciado!', result);

                        startBtn.textContent = 'Parar Bot';
                        startBtn.classList.add('running');
                        window.botRunning = true;

                        // ✅ USA MODAL CORRETO: botRunningModal
                        const modal = document.getElementById('botRunningModal');
                        if (modal) {
                            modal.classList.add('active');
                            console.log('✅ Modal botRunningModal aberto!');

                            // Atualizar informações do modal
                            const profitEl = document.getElementById('botRunningProfit');
                            const saldoEl = document.getElementById('botRunningSaldo');
                            const statusEl = document.getElementById('botStatusText');

                            if (profitEl) profitEl.textContent = '$0 (0%)';
                            if (saldoEl) saldoEl.textContent = '$0.02';
                            if (statusEl) statusEl.textContent = 'Buscando trades';
                        } else {
                            console.error('❌ Modal botRunningModal não encontrado!');
                        }
                    } else {
                        throw new Error(result.error || result.message || 'Erro desconhecido');
                    }

                } catch (error) {
                    console.error('❌ Erro ao iniciar:', error);
                    startBtn.textContent = 'Iniciar Bot';
                } finally {
                    startBtn.disabled = false;
                }
            }
        };

        startBtn.setAttribute('data-event-added', 'true');
        console.log('✅ Botão startButton configurado!');
    }
}

// ==========================================
// DASHBOARD FUNCTIONS
// ==========================================

const Dashboard = {
    updateInterval: null,
    botRunning: false
};

function initDashboard() {
    console.log('🎨 Inicializando Dashboard...');

    const startButton = document.getElementById('startButton');
    if (startButton) {
        startButton.addEventListener('click', toggleBot);
    }

    updateDashboardBalance();
    console.log('✅ Dashboard inicializado!');
}

window.toggleBot = async function(event) {
    if (event && event.preventDefault) {
        event.preventDefault();
    }

    console.log(`🎯 toggleBot() chamado`);

    const button = document.getElementById('iaStartBtn') || document.getElementById('startButton');

    if (!button) {
        console.error('❌ Botão não encontrado!');
        return;
    }

    const botType = 'ia';

    if (window.SystemState && window.SystemState.bots && window.SystemState.bots[botType]) {
        await stopBot(button, botType);
    } else {
        await startBot(button, botType);
    }
};

async function startBot(button, botType) {
    console.log('🚀 startBot chamado');
}

async function stopBot(button, botType) {
    console.log('🛑 stopBot chamado');
}

async function updateDashboardBalance() {
    // Implementação...
}

function updateBalanceDisplay(balance) {
    const topBalance = document.getElementById('topBalance');
    if (topBalance) {
        topBalance.textContent = `$ ${balance.toFixed(2)}`;
    }

    const panels = document.querySelectorAll('.balance-display');
    panels.forEach(panel => {
        panel.textContent = `$ ${balance.toFixed(2)}`;
    });
}

function showNotification(message, type = 'info') {
    console.log(`[${type}] ${message}`);
}

function addLog(message, type = 'info') {
    if (!window.AlphaDolar) {
        window.AlphaDolar = { logs: [] };
    }

    const log = {
        time: new Date().toLocaleTimeString(),
        message,
        type
    };

    window.AlphaDolar.logs.unshift(log);

    if (window.AlphaDolar.logs.length > 100) {
        window.AlphaDolar.logs = window.AlphaDolar.logs.slice(0, 100);
    }

    console.log(`[${type.toUpperCase()}] ${message}`);
}

// ==========================================
// INICIALIZAÇÃO
// ==========================================

document.addEventListener('DOMContentLoaded', async () => {
    console.log('🎯 Inicializando Alpha Dolar 2.0...');

    const isTradingPage = document.getElementById('tradingview_chart') !== null;
    const isDashboardPage = document.getElementById('demo-btn') !== null;

    console.log(`📄 Página: ${isTradingPage ? 'trading.html' : isDashboardPage ? 'dashboard_v2.html' : 'desconhecida'}`);

    if (isDashboardPage) {
        await initAccountMode();
        setupAccountModeListeners();
        initDashboard();
    }

    if (isTradingPage) {
        setTimeout(() => {
            setupTradingButton();
        }, 500);
    }

    const clearBtn = document.getElementById('clearHistory');
    if (clearBtn) {
        clearBtn.addEventListener('click', () => {
            const tbody = document.getElementById('historyBody');
            if (tbody) {
                tbody.innerHTML = '';
                showNotification('🗑️ Histórico limpo', 'info');
            }
        });
    }

    console.log('✅ Sistema pronto!');
});

console.log('✅ dashboard-v3.js (CORRIGIDO) carregado!');