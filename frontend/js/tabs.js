/**
 * TABS.JS - TradingView com Bitcoin (TESTADO E FUNCIONANDO)
 */

// ==========================================
// TABS CONTROL
// ==========================================

document.addEventListener('DOMContentLoaded', function() {
    console.log('📑 Tabs.js carregado');

    initializeTabs();

    // Aguarda 500ms para garantir que DOM está pronto
    setTimeout(initializeTradingView, 500);
});

// Inicializar tabs
function initializeTabs() {
    const tabs = document.querySelectorAll('.center-tab');
    const panes = document.querySelectorAll('.tab-pane');

    tabs.forEach(tab => {
        tab.addEventListener('click', function() {
            const tabName = this.dataset.tab;

            // Remove active de todas as tabs
            tabs.forEach(t => t.classList.remove('active'));
            panes.forEach(p => p.classList.remove('active'));

            // Adiciona active na tab clicada
            this.classList.add('active');

            // Mostra o painel correspondente
            const targetPane = document.getElementById(`tab-${tabName}`);
            if (targetPane) {
                targetPane.classList.add('active');
                console.log(`📑 Tab ativada: ${tabName}`);
            }
        });
    });
}

// ==========================================
// TRADINGVIEW INTEGRATION (CÓDIGO QUE FUNCIONOU)
// ==========================================

function initializeTradingView() {
    // Verificar se TradingView está disponível
    if (typeof TradingView === 'undefined') {
        console.warn('⚠️ TradingView não carregado, tentando novamente em 1s...');
        setTimeout(initializeTradingView, 1000);
        return;
    }

    const chartContainer = document.getElementById('tradingview_chart');

    if (!chartContainer) {
        console.error('❌ Container tradingview_chart não encontrado');
        return;
    }

    try {
        console.log('🚀 Inicializando TradingView...');

        // LIMPA O CONTAINER (IGUAL O CONSOLE)
        chartContainer.innerHTML = '';

        // CRIA O WIDGET (EXATAMENTE COMO FUNCIONOU NO CONSOLE)
        new TradingView.widget({
            "width": "100%",
            "height": "100%",
            "symbol": "BINANCE:BTCUSDT",
            "interval": "5",
            "timezone": "America/Sao_Paulo",
            "theme": "dark",
            "style": "1",
            "locale": "pt_BR",
            "container_id": "tradingview_chart"
        });

        console.log('✅ TradingView carregado com Bitcoin!');

        // Log para dashboard
        if (typeof addLog === 'function') {
            addLog('📊 Gráfico TradingView carregado', 'success');
        }

    } catch (error) {
        console.error('❌ Erro ao inicializar TradingView:', error);

        // Mostra erro no container
        chartContainer.innerHTML = `
            <div style="
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                height: 100%;
                background: #1a1d2e;
                color: rgba(255,255,255,0.6);
                padding: 40px;
                text-align: center;
            ">
                <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="margin-bottom: 20px;">
                    <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline>
                </svg>
                <p style="font-size: 14px; margin-bottom: 8px; color: #fff;">Erro ao carregar gráfico</p>
                <small style="font-size: 11px; opacity: 0.5;">${error.message}</small>
                <button onclick="location.reload()" style="
                    margin-top: 20px;
                    padding: 10px 20px;
                    background: #42A5F5;
                    border: none;
                    border-radius: 6px;
                    color: white;
                    cursor: pointer;
                    font-size: 13px;
                    font-weight: 600;
                ">Recarregar Página</button>
            </div>
        `;
    }
}

// ==========================================
// CHANGE SYMBOL (DESABILITADO)
// ==========================================

function changeTradingViewSymbol(symbol) {
    console.log(`📊 Mercado selecionado: ${symbol}`);
    console.log('ℹ️ Gráfico mantém Bitcoin como referência');

    // Nota: Mantemos Bitcoin fixo porque:
    // 1. Os símbolos Deriv (R_10, R_25, etc) não existem no TradingView
    // 2. Bitcoin funciona 100% e é volátil como os mercados Deriv
    // 3. Serve como referência visual enquanto o bot opera nos mercados reais
}

console.log('✅ Tabs.js carregado!');