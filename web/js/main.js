/**
 * ALPHA DOLAR 2.0 - Main Script (Simplificado)
 * Apenas inicialização, sem carregar componentes
 */

// ✅ GARANTIR QUE API_BASE_URL EXISTE - PRIMEIRO DE TUDO!
if (!window.API_BASE_URL) {
    window.API_BASE_URL = 'https://alpha-dolar-backend.onrender.com';
    console.log('⚠️ API_BASE_URL definida pelo main.js');
}

if (!window.botRunning) {
    window.botRunning = false;
}

// Estado global
window.AlphaDolar = {
    currentMode: 'manual',
    currentIAMode: 'simples',
    botRunning: false,
    logs: [],
    history: [],
    stats: {
        lucro_liquido: 0,
        saldo_atual: 0.92,
        total_trades: 0,
        vitorias: 0,
        derrotas: 0,
        win_rate: 0
    }
};

// ==========================================
// LOGS
// ==========================================
function addLog(message, type = 'info') {
    const log = {
        time: new Date().toLocaleTimeString(),
        message,
        type,
        id: Date.now()
    };
    AlphaDolar.logs.unshift(log);
    if (AlphaDolar.logs.length > 100) {
        AlphaDolar.logs = AlphaDolar.logs.slice(0, 100);
    }
    console.log(`[${type.toUpperCase()}] ${message}`);
}

// ==========================================
// MODAL HELPERS
// ==========================================
function showModal() {
    const modal = document.getElementById('opModal');
    if (modal) {
        modal.classList.add('active');
        startProgressAnimation();
    }
}

function hideModal() {
    const modal = document.getElementById('opModal');
    if (modal) {
        modal.classList.remove('active');
    }
}

function startProgressAnimation() {
    // Animation logic here if needed
}

// ==========================================
// INICIALIZAÇÃO
// ==========================================
window.addEventListener('DOMContentLoaded', async () => {
    console.log('🚀 Iniciando Alpha Dolar 2.0...');

    // Log inicial
    addLog('🚀 Alpha Dolar 2.0 iniciado', 'success');
    addLog('📡 Sistema pronto', 'info');

    console.log('✅ Alpha Dolar 2.0 pronto!');
});