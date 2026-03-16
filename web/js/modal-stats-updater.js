/**
 * MODAL-STATS-UPDATER.JS — Alpha Dolar 2.0
 * Observa o modal e atualiza stats em tempo real
 * CORRIGIDO: remove conflito com stopBotBtn e alert() indesejado
 */

(function() {
    const API_URL = 'https://alpha-dolar-backend.onrender.com/api';
    let statsInterval = null;

    // ---- Atualiza stats do modal ----
    async function updateModalStats() {
        try {
            const res = await fetch(`${API_URL}/bot/stats/ia`);
            if (!res.ok) return;
            const data = await res.json();
            if (!data.success) return;

            const stats = data.stats || data;

            // Lucro
            const profitEl = document.getElementById('botRunningProfit');
            if (profitEl) {
                const profit  = parseFloat(stats.saldo_liquido || stats.profit || 0);
                const balance = parseFloat(stats.balance || stats.saldo_atual || 0);
                const pct     = balance > 0 ? ((profit / balance) * 100).toFixed(1) : '0.0';
                profitEl.textContent = `$${profit.toFixed(2)} (${pct}%)`;
                profitEl.style.color = profit >= 0 ? '#4caf50' : '#ef4444';
            }

            // Saldo
            const saldoEl = document.getElementById('botRunningSaldo');
            if (saldoEl) {
                const saldo = parseFloat(stats.balance || stats.saldo_atual || 0);
                if (saldo > 0) saldoEl.textContent = `$${saldo.toFixed(2)}`;
            }

            // Status text (não sobrescreve se já foi definido pelo controlador principal)
            const trades = stats.total_trades || 0;
            const wr     = stats.win_rate || 0;
            const statusEl = document.getElementById('botStatusText');
            if (statusEl && trades > 0) {
                statusEl.textContent = `Trades: ${trades} | Win: ${wr.toFixed ? wr.toFixed(1) : wr}%`;
            }

        } catch (err) {
            // silencioso
        }
    }

    function startStatsUpdater() {
        updateModalStats();
        if (statsInterval) clearInterval(statsInterval);
        statsInterval = setInterval(updateModalStats, 3000);
    }

    function stopStatsUpdater() {
        if (statsInterval) {
            clearInterval(statsInterval);
            statsInterval = null;
        }
    }

    // Observa abertura/fechamento do modal
    function observeModal() {
        const modal = document.getElementById('botRunningModal');
        if (!modal) return;

        const observer = new MutationObserver(() => {
            if (modal.classList.contains('active')) {
                startStatsUpdater();
            } else {
                stopStatsUpdater();
            }
        });

        observer.observe(modal, { attributes: true, attributeFilter: ['class'] });
    }

    // ✅ CORRIGIDO: NÃO sobrescreve stopBotFromModal com alert()
    // O controle do botão Parar fica 100% no dashboard-fixed.html
    // Este arquivo apenas observa e atualiza dados visuais

    function init() {
        // Garante modal oculto no início
        const modal = document.getElementById('botRunningModal');
        if (modal) modal.classList.remove('active');
        observeModal();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    setTimeout(init, 500);

})();