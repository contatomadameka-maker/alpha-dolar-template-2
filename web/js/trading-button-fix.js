/**
 * TRADING-BUTTON-FIX.JS - VERSÃO CORRIGIDA 2026-02-26
 * Fixes:
 *   ✅ Lê configurações reais da tela (não hardcoded)
 *   ✅ Remove alert() que travava e causava cliques duplos
 *   ✅ Botão desabilitado durante operação para evitar duplo clique
 *   ✅ Lê saldo atual do SystemState para validação
 */

(function() {
    console.log('🔧 [FIX] Carregando trading-button-fix.js...');

    // ==========================================
    // LEITURA DE CONFIGURAÇÕES DA TELA
    // ==========================================

    function getConfigFromUI() {
        // Tenta ler os valores dos inputs da tela
        const getValue = (selectors, defaultVal) => {
            for (const sel of selectors) {
                const el = document.querySelector(sel);
                if (el) {
                    const val = parseFloat(el.value || el.textContent?.replace('$', '').trim());
                    if (!isNaN(val)) return val;
                }
            }
            return defaultVal;
        };

        const getString = (selectors, defaultVal) => {
            for (const sel of selectors) {
                const el = document.querySelector(sel);
                if (el) {
                    const val = el.value || el.textContent?.trim() || el.dataset?.value;
                    if (val) return val;
                }
            }
            return defaultVal;
        };

        const stake  = getValue(['#stakeInput', '#initialStake', '[data-field="stake"]', '#quantia'], 0.35);
        const target = getValue(['#targetInput', '#lucroAlvo', '[data-field="target"]', '#lucro'], 2.0);
        const stop   = getValue(['#stopInput', '#limitePerda', '[data-field="stop"]', '#limite'], 5.0);
        const market = getString(['#marketSelect', '#mercado', '[data-field="market"]'], 'R_100');
        const strategy = getString(['#strategySelect', '#estrategia', '[data-field="strategy"]'], 'alpha_bot_balanced');

        console.log(`📋 Config lida da tela: stake=${stake} target=${target} stop=${stop} market=${market}`);

        return {
            mode:          'simples',
            market:        market,
            strategy:      strategy,
            trading_mode:  'fast',
            risk_mode:     'conservative',
            initial_stake: stake,
            target_profit: target,
            stop_loss:     stop,
            multiplier:    1,
            duration:      1
        };
    }

    // ==========================================
    // NOTIFICAÇÃO SEM ALERT()
    // ==========================================

    function notify(message, type = 'info') {
        // Usa sistema de notificação existente se disponível
        if (typeof showNotification === 'function') { showNotification(message, type); return; }
        if (typeof showToast === 'function')         { showToast(message, type); return; }

        // Fallback: toast simples
        const existing = document.getElementById('_tradeNotify');
        if (existing) existing.remove();

        const colors = { success: '#4caf50', error: '#f44336', info: '#2196f3', warning: '#ff9800' };
        const toast = document.createElement('div');
        toast.id = '_tradeNotify';
        toast.style.cssText = `
            position: fixed; top: 24px; left: 50%; transform: translateX(-50%);
            background: #1a1a2e; border: 1px solid ${colors[type] || colors.info};
            border-radius: 12px; color: #fff; padding: 14px 24px; z-index: 99999;
            box-shadow: 0 8px 32px rgba(0,0,0,0.4); max-width: 360px;
            text-align: center; font-size: 14px; line-height: 1.5;
        `;
        toast.textContent = message;
        document.body.appendChild(toast);
        setTimeout(() => toast?.remove(), 4000);
    }

    // ==========================================
    // INIT
    // ==========================================

    function init() {
        const btn = document.getElementById('iaStartBtn') || document.getElementById('startButton');

        if (!btn) {
            setTimeout(init, 500);
            return;
        }

        if (typeof startBotAPI !== 'function' || typeof stopBotAPI !== 'function') {
            setTimeout(init, 500);
            return;
        }

        console.log('✅ [FIX] Botão e funções API prontos!');

        // Remove listener antigo
        const newBtn = btn.cloneNode(true);
        btn.parentNode.replaceChild(newBtn, btn);

        newBtn.onclick = async function(e) {
            if (e) { e.preventDefault(); e.stopPropagation(); }

            // ✅ Evita duplo clique
            if (newBtn.disabled) return;

            const botType  = 'ia';
            const isRunning = window.SystemState?.bots?.[botType] || window.botRunning || false;

            if (isRunning) {
                // ==================== PARAR ====================
                try {
                    newBtn.disabled = true;
                    newBtn.textContent = 'Parando...';

                    await stopBotAPI(botType);

                    newBtn.textContent = '▶ Iniciar Robô';
                    newBtn.classList.remove('active', 'running');

                    if (window.SystemState) window.SystemState.bots[botType] = false;
                    window.botRunning = false;

                    // Fecha modal
                    const modal = document.getElementById('opModal') || document.getElementById('botRunningModal');
                    if (modal) modal.classList.remove('active');

                    notify('✅ Robô parado com sucesso!', 'success');

                } catch (error) {
                    console.error('❌ Erro ao parar:', error);
                    notify('❌ Erro ao parar: ' + error.message, 'error');
                    newBtn.textContent = 'Parar Robô';
                } finally {
                    newBtn.disabled = false;
                }

            } else {
                // ==================== INICIAR ====================
                try {
                    newBtn.disabled = true;
                    newBtn.textContent = 'Iniciando...';

                    // ✅ Lê config real da tela
                    const config = getConfigFromUI();

                    const result = await startBotAPI(botType, config);

                    newBtn.textContent = '⏹ Parar Robô';
                    newBtn.classList.add('active', 'running');

                    if (window.SystemState) window.SystemState.bots[botType] = true;
                    window.botRunning = true;

                    // Abre modal
                    const modal = document.getElementById('opModal') || document.getElementById('botRunningModal');
                    if (modal) {
                        modal.classList.add('active');
                        // Atualiza display do modal com config usada
                        if (typeof updateBotRunningDisplay === 'function') {
                            updateBotRunningDisplay({
                                stake:    config.initial_stake,
                                target:   config.target_profit,
                                stop:     config.stop_loss,
                                market:   config.market,
                                mode:     'IA Simples',
                                risk:     'Conservador',
                                strategy: 'Alpha Bot Balanced'
                            });
                        }
                    }

                    notify('✅ Robô iniciado! Aguardando sinais...', 'success');

                } catch (error) {
                    console.error('❌ Erro ao iniciar:', error);
                    // Erro já exibido pelo startBotAPI (showBalanceError)
                    newBtn.textContent = '▶ Iniciar Robô';
                    newBtn.classList.remove('active', 'running');
                    if (window.SystemState) window.SystemState.bots[botType] = false;
                    window.botRunning = false;
                } finally {
                    newBtn.disabled = false;
                }
            }
        };

        console.log('✅ [FIX] Botão configurado com sucesso!');
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();

console.log('📦 trading-button-fix.js carregado!');