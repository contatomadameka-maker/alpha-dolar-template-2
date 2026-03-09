/**
 * BOT RUNNING MODAL — Alpha Dolar 2.0
 * CORRIGIDO: remove alert(), remove conflito com stopBotBtn do dashboard-fixed.html
 */

// Abre modal
function openBotRunningModal(config) {
    const modal = document.getElementById('botRunningModal');
    if (!modal) return;
    if (config) updateBotRunningDisplay(config);
    modal.classList.add('active');
    startProgressAnimation();
}

// Fecha modal
function closeBotRunningModal() {
    const modal = document.getElementById('botRunningModal');
    if (modal) modal.classList.remove('active');
    stopProgressAnimation();
}

// Atualiza display das configurações
function updateBotRunningDisplay(config) {
    const set = (id, val) => {
        const el = document.getElementById(id);
        if (el && val !== undefined) el.textContent = val;
    };

    if (config.stake)    set('botDisplayStake',    `$${config.stake}`);
    if (config.target)   set('botDisplayTarget',   `$${config.target}`);
    if (config.stop)     set('botDisplayStop',     `$${config.stop}`);
    if (config.market)   set('botDisplayMarket',   config.market);
    if (config.mode)     set('botDisplayMode',     config.mode);
    if (config.risk)     set('botDisplayRisk',     config.risk);

    // ✅ CORRIGIDO: não substitui "Alpha Bot" por "DC Bot"
    if (config.strategy) set('botDisplayStrategy', config.strategy);
}

// Atualiza lucro e saldo
function updateBotRunningStats(stats) {
    if (stats.lucro_liquido !== undefined) {
        const profitEl = document.getElementById('botRunningProfit');
        if (profitEl) {
            const profit = stats.lucro_liquido;
            const pct    = stats.win_rate || 0;
            profitEl.textContent = `$${profit.toFixed(2)} (${pct.toFixed(1)}%)`;
            profitEl.style.color = profit >= 0 ? '#4caf50' : '#f44336';
        }
    }

    if (stats.saldo_atual !== undefined) {
        const saldoEl = document.getElementById('botRunningSaldo');
        if (saldoEl) saldoEl.textContent = `$${stats.saldo_atual.toFixed(2)}`;
    }
}

// Animação da progress bar (segmentos)
function startProgressAnimation() {
    const segments = document.querySelectorAll('.progress-segment');
    if (!segments.length) return;
    segments.forEach((s, i) => {
        s.classList.remove('active', 'loading');
        if (i < 2) s.classList.add('active');
        if (i === 1) s.classList.add('loading');
    });
}

function stopProgressAnimation() {
    document.querySelectorAll('.progress-segment').forEach(s => {
        s.classList.remove('active', 'loading');
    });
}

// ✅ CORRIGIDO: stopBotFromModal NÃO faz chamada de API diretamente
// Apenas dispara o click no botão principal que já tem toda a lógica
// Isso evita duplicação e conflito com o listener do dashboard-fixed.html
window.stopBotFromModal = function() {
    // Tenta o botão de parar do modal primeiro (tem listener no dashboard-fixed.html)
    const stopBtn = document.getElementById('stopBotBtn');
    if (stopBtn) {
        stopBtn.click();
        return;
    }
    // Fallback: botão principal
    const startBtn = document.getElementById('startButton');
    if (startBtn && startBtn.innerText.includes('Parar')) {
        startBtn.click();
    }
};

console.log('✅ Bot Running Modal carregado!');