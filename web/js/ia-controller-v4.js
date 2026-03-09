/**
 * ALPHA DOLAR 2.0 - IA Controller (Apenas UI/Modals)
 * Versão Limpa - Sem conflito com dashboard.js
 */

// ==================== ESTADO GLOBAL ====================

let currentIAState = {
    mode: 'simples',
    market: {
        id: 'R_100',
        name: 'Volatility 100 Index',
        number: '100',
        description: 'Volatilidade constante de 100%'
    },
    strategy: {
        id: 'alpha_bot_1',
        name: 'Alpha Bot 1',
        icon: '📊'
    },
    tradingMode: {
        id: 'fast',
        name: 'Veloz',
        icon: '⚡'
    },
    riskMode: {
        id: 'conservative',
        name: 'Conservador',
        icon: '🛡️',
        color: '#10b981',
        risk_level: 'Baixo risco'
    },
    stake: 1,
    target: 20,
    stopLoss: 1000,
    stopLossMode: 'value',
    balance: 10000,
    profit: 0,
    profitPercentage: 0
};

let marketsData = null;
let strategiesData = null;
let riskModesData = null;

// ==================== INICIALIZAÇÃO ====================

async function loadIAData() {
    try {
        console.log('🔄 Carregando dados IA...');

        const [markets, strategies, riskModes] = await Promise.all([
            fetch('data/markets.json').then(r => r.json()),
            fetch('data/strategies.json?v=' + Date.now()).then(r => r.json()),
            fetch('data/risk-modes.json').then(r => r.json())
        ]);

        marketsData = markets;
        strategiesData = strategies;
        riskModesData = riskModes;

        populateMarkets();
        populateStrategies();
        populateRiskModes();
        updateAllDisplays();

        console.log('✅ Dados IA carregados!');
    } catch (error) {
        console.error('❌ Erro:', error);
    }
}

// ==================== POPULAR MODAIS ====================

function populateMarkets() {
    if (!marketsData) return;

    const containers = {
        continuous: document.getElementById('continuousMarkets'),
        daily_reset: document.getElementById('dailyResetMarkets'),
        jump: document.getElementById('jumpMarkets')
    };

    if (containers.continuous) {
        containers.continuous.innerHTML = '';
        marketsData.continuous?.forEach(market => {
            const div = document.createElement('div');
            div.className = 'market-item';
            div.onclick = () => selectMarket(market);
            div.innerHTML = `
                <div class="market-item-icon">
                    ${market.icon || `<span class="market-number">${market.number}</span>`}
                    ${market.badge ? `<span class="market-badge-1s">${market.badge}</span>` : ''}
                </div>
                <div class="market-item-name">${market.name}</div>
            `;
            containers.continuous.appendChild(div);
        });
    }

    if (containers.daily_reset) {
        containers.daily_reset.innerHTML = '';
        marketsData.daily_reset?.forEach(market => {
            const div = document.createElement('div');
            div.className = 'market-item';
            div.onclick = () => selectMarket(market);
            div.innerHTML = `
                <div class="market-item-icon">${market.icon || '📈'}</div>
                <div class="market-item-name">${market.name}</div>
            `;
            containers.daily_reset.appendChild(div);
        });
    }

    if (containers.jump) {
        containers.jump.innerHTML = '';
        marketsData.jump?.forEach(market => {
            const div = document.createElement('div');
            div.className = 'market-item';
            div.onclick = () => selectMarket(market);
            div.innerHTML = `
                <div class="market-item-icon">⚡<span class="market-number">${market.number}</span></div>
                <div class="market-item-name">${market.name}</div>
            `;
            containers.jump.appendChild(div);
        });
    }
}

function populateStrategies() {
    if (!strategiesData) return;

    const containers = {
        free: document.getElementById('freeStrategies'),
        vip: document.getElementById('vipStrategies'),
        premium: document.getElementById('premiumStrategies')
    };

    if (containers.free) {
        containers.free.innerHTML = '';
        strategiesData.free?.forEach(s => containers.free.appendChild(createStrategyItem(s)));
    }

    if (containers.vip) {
        containers.vip.innerHTML = '';
        strategiesData.vip?.forEach(s => containers.vip.appendChild(createStrategyItem(s)));
    }

    if (containers.premium) {
        containers.premium.innerHTML = '';
        strategiesData.premium?.forEach(s => containers.premium.appendChild(createStrategyItem(s)));
    }
}

function createStrategyItem(strategy) {
    const div = document.createElement('div');
    div.className = `strategy-item ${strategy.locked ? 'locked' : ''} ${strategy.active ? 'active' : ''}`;

    if (!strategy.locked) {
        div.onclick = () => selectStrategy(strategy);
    }

    const badges = strategy.badges || (strategy.badge ? [strategy.badge] : []);
    const badgeHTML = badges.map(b => `<span class="badge-${b.toLowerCase().replace(' ', '-')}">${b}</span>`).join('');
    const lockHTML = strategy.locked ? '<i class="fas fa-lock lock-icon"></i>' : '';
    const checkHTML = strategy.active && !strategy.locked ? '<i class="fas fa-check active-check"></i>' : '';

    div.innerHTML = `
        <div class="strategy-item-icon">${strategy.icon}</div>
        <div class="strategy-item-name">${strategy.name}</div>
        ${badgeHTML}
        ${lockHTML}
        ${checkHTML}
    `;

    return div;
}

function populateRiskModes() {
    if (!riskModesData) return;

    const container = document.getElementById('riskModeList');
    if (!container) return;

    container.innerHTML = '';

    // Suporta dois formatos: {modes: [...]} ou [...]
    const modes = Array.isArray(riskModesData) ? riskModesData : (riskModesData.modes || []);

    if (modes.length === 0) {
        console.warn('⚠️ Nenhum modo de risco encontrado');
        return;
    }

    modes.forEach(mode => {
        const div = document.createElement('div');
        div.className = 'risk-mode-item';
        if (mode.id === 'conservative') div.classList.add('active');
        div.onclick = () => selectRiskMode(mode);

        div.innerHTML = `
            <div class="risk-mode-icon" style="background: ${mode.color}">${mode.icon}</div>
            <div class="risk-mode-content">
                <div class="risk-mode-title">${mode.name}</div>
                <div class="risk-mode-level" style="color: ${mode.color}">🔺 ${mode.risk_level || 'Médio risco'}</div>
                <div class="risk-mode-min">Valor recomendado: no mínimo $${mode.min_balance}</div>
            </div>
            ${mode.id === 'conservative' ? '<i class="fas fa-check risk-check"></i>' : ''}
        `;

        container.appendChild(div);
    });

    console.log(`✅ ${modes.length} modos de risco carregados`);
}

// ==================== SELEÇÃO ====================

function selectMarket(market) {
    console.log('✅ Mercado:', market.name);
    currentIAState.market = market;
    updateMarketDisplay();
    closeMarketModal();
}

// Função GLOBAL para modals.js chamar
window.selectMarketGlobal = selectMarket;

function selectStrategy(strategy) {
    console.log('✅ Estratégia:', strategy.name);
    currentIAState.strategy = strategy;
    updateStrategyDisplay();
    closeStrategyModal();
}

// Função GLOBAL para modals.js chamar
window.selectStrategyGlobal = selectStrategy;

function selectTradingMode(modeId, icon, name) {
    console.log('✅ Modo negociação:', name);
    currentIAState.tradingMode = { id: modeId, name: name, icon: icon };
    updateTradingModeDisplay();
    closeTradingModeModal();

    document.querySelectorAll('.mode-option').forEach(item => {
        item.classList.remove('active');
    });
    const selected = document.querySelector(`[data-mode="${modeId}"]`);
    if (selected) selected.classList.add('active');
}

function selectRiskMode(mode) {
    console.log('✅ Risco:', mode.name);
    currentIAState.riskMode = mode;
    updateRiskModeDisplay();
    // NÃO fecha aqui - modals.js já fecha!
}

// Função GLOBAL para modals.js chamar
window.selectRiskModeGlobal = selectRiskMode;

function selectStopLossMode(mode) {
    currentIAState.stopLossMode = mode;
    document.querySelectorAll('input[name="stopLossMode"]').forEach(radio => {
        radio.checked = radio.value === mode;
    });
}

// ==================== ATUALIZAR DISPLAYS ====================

function updateAllDisplays() {
    updateMarketDisplay();
    updateStrategyDisplay();
    updateTradingModeDisplay();
    updateRiskModeDisplay();
    updateProfitDisplay();
}

function updateMarketDisplay() {
    const market = currentIAState.market;
    const nameEl = document.getElementById('selectedMarket'); // ID correto!
    const hintEl = document.getElementById('marketHint');

    if (nameEl) {
        nameEl.textContent = market.name;
        console.log('✅ Mercado atualizado no display:', market.name);
    }
    if (hintEl) {
        hintEl.textContent = market.description || '';
    }
}

function updateStrategyDisplay() {
    const strategy = currentIAState.strategy;
    const nameEl = document.getElementById('selectedStrategy'); // ID correto!

    if (nameEl) {
        nameEl.textContent = strategy.name;
        console.log('✅ Estratégia atualizada no display:', strategy.name);
    }
}

function updateTradingModeDisplay() {
    const mode = currentIAState.tradingMode;
    const nameEl = document.getElementById('selectedMode'); // ID correto!
    const descEl = document.getElementById('modeDesc');

    if (nameEl) {
        nameEl.textContent = mode.name;
        console.log('✅ Modo de negociação atualizado no display:', mode.name);
    }
    if (descEl) {
        descEl.textContent = getModeDescription(mode.id);
    }
}

function getModeDescription(modeId) {
    const descriptions = {
        'lowRisk': 'Máxima precisão, menos negociações',
        'accurate': 'Menos negociações, mais precisão',
        'balanced': 'Negociações e precisão balanceada',
        'faster': 'Mais negociações, menos precisão'
    };
    return descriptions[modeId] || '';
}

function updateRiskModeDisplay() {
    const risk = currentIAState.riskMode;
    console.log('🔄 Atualizando risco:', risk.name);

    const cards = Array.from(document.querySelectorAll('[onclick]')).filter(el =>
        el.getAttribute('onclick')?.includes('openRiskModal')
    );

    cards.forEach(card => {
        card.innerHTML = '';

        const iconDiv = document.createElement('div');
        iconDiv.style.cssText = `width: 36px; height: 36px; border-radius: 50%; background: ${risk.color}; display: flex; align-items: center; justify-content: center; font-size: 1rem; flex-shrink: 0;`;
        iconDiv.textContent = risk.icon;

        const contentDiv = document.createElement('div');
        contentDiv.style.cssText = 'flex: 1;';

        const nameDiv = document.createElement('div');
        nameDiv.style.cssText = 'font-weight: 700; font-size: 0.8rem;';
        nameDiv.textContent = risk.name;

        const levelDiv = document.createElement('div');
        levelDiv.style.cssText = `font-size: 0.65rem; color: ${risk.color};`;
        levelDiv.textContent = `🔺 ${risk.risk_level}`;

        contentDiv.appendChild(nameDiv);
        contentDiv.appendChild(levelDiv);

        const chevron = document.createElement('i');
        chevron.className = 'fas fa-chevron-right';
        chevron.style.cssText = 'font-size: 0.7rem;';

        card.appendChild(iconDiv);
        card.appendChild(contentDiv);
        card.appendChild(chevron);

        card.onclick = openRiskModal;

        console.log('✅ Card risco atualizado:', risk.name, risk.color);
    });
}

function updateProfitDisplay() {
    const profitEl = document.getElementById('iaCurrentProfit');
    if (profitEl) {
        profitEl.textContent = `$${currentIAState.profit.toFixed(2)} (${currentIAState.profitPercentage.toFixed(2)}%)`;
    }
}

// ==================== MODAIS ====================

function openMarketModal() {
    document.getElementById('marketModal')?.classList.add('active');
}

function closeMarketModal() {
    document.getElementById('marketModal')?.classList.remove('active');
}

function openStrategyModal() {
    document.getElementById('strategyModal')?.classList.add('active');
}

function closeStrategyModal() {
    document.getElementById('strategyModal')?.classList.remove('active');
}

function openTradingModeModal() {
    console.log('🚀 Abrindo modal modo negociação');
    document.getElementById('tradingModeModal')?.classList.add('active');
}

function closeTradingModeModal() {
    console.log('❌ Fechando modal modo negociação');
    document.getElementById('tradingModeModal')?.classList.remove('active');
}

function openRiskModal() {
    console.log('🚀 Abrindo modal risco');
    document.getElementById('riskModal')?.classList.add('active');
}

function closeRiskModal() {
    console.log('❌ Fechando modal risco');
    document.getElementById('riskModal')?.classList.remove('active');
}

function openStopLossModal() {
    document.getElementById('stopLossModal')?.classList.add('active');
}

function closeStopLossModal() {
    document.getElementById('stopLossModal')?.classList.remove('active');
}

// Fechar modal clicando fora
document.addEventListener('click', function(event) {
    if (event.target.classList.contains('modal-overlay')) {
        event.target.classList.remove('active');
    }
});

// ==================== TOGGLE MODE ====================

function switchIAComplexity(mode) {
    currentIAState.mode = mode;

    document.querySelectorAll('.toggle-btn').forEach(btn => {
        btn.classList.remove('active');
        if (btn.dataset.mode === mode) {
            btn.classList.add('active');
        }
    });

    document.querySelectorAll('.ia-config-panel').forEach(panel => {
        panel.classList.remove('active');
    });

    const targetPanel = document.getElementById(`ia-${mode}-config`);
    if (targetPanel) {
        targetPanel.classList.add('active');
    }
}

// ==================== TOGGLE IA MODE (SIMPLES/AVANÇADO) ====================

window.toggleIAMode = function(mode) {
    console.log('🔄 Alternando modo IA:', mode);

    currentIAState.mode = mode;

    // Atualizar botões
    document.querySelectorAll('.ia-toggle button').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');

    // Mostrar/ocultar painéis
    document.getElementById('iaSimples').style.display = mode === 'simples' ? 'block' : 'none';
    document.getElementById('iaAvancado').style.display = mode === 'avancado' ? 'block' : 'none';
};

// ==================== INICIALIZAR ====================

document.addEventListener('DOMContentLoaded', loadIAData);

console.log('✅ IA Controller carregado (versão limpa)!');