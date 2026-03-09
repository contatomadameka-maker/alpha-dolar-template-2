/**
 * MODALS.JS - Sistema de Modais INTEGRADO com IA Controller
 */

// ==========================================
// SVG ICONS
// ==========================================

const SVG_ICONS = {
    'volatility': `<svg width="24" height="24" viewBox="0 0 24 24" fill="none">
        <rect x="3" y="12" width="2" height="8" fill="#42A5F5" rx="1"/>
        <rect x="7" y="8" width="2" height="12" fill="#42A5F5" rx="1"/>
        <rect x="11" y="4" width="2" height="16" fill="#42A5F5" rx="1"/>
        <rect x="15" y="10" width="2" height="10" fill="#42A5F5" rx="1"/>
        <rect x="19" y="14" width="2" height="6" fill="#42A5F5" rx="1"/>
    </svg>`,
    'jump': `<svg width="24" height="24" viewBox="0 0 24 24" fill="none">
        <path d="M3 18L7 14L9 16L13 12L15 14L21 8" stroke="#ff9800" stroke-width="2" stroke-linecap="round"/>
        <circle cx="7" cy="14" r="2" fill="#ff9800"/>
        <circle cx="15" cy="14" r="2" fill="#ff9800"/>
    </svg>`,
    'bear': `<svg width="24" height="24" viewBox="0 0 24 24" fill="none">
        <path d="M20 4L4 20" stroke="#f44336" stroke-width="2" stroke-linecap="round"/>
        <path d="M20 4L20 12M20 4L12 4" stroke="#f44336" stroke-width="2" stroke-linecap="round"/>
    </svg>`,
    'bull': `<svg width="24" height="24" viewBox="0 0 24 24" fill="none">
        <path d="M4 20L20 4" stroke="#4caf50" stroke-width="2" stroke-linecap="round"/>
        <path d="M20 4L20 12M20 4L12 4" stroke="#4caf50" stroke-width="2" stroke-linecap="round"/>
    </svg>`,
    'forex': `<svg width="24" height="24" viewBox="0 0 24 24" fill="none">
        <text x="3" y="16" font-size="14" font-weight="bold" fill="#42A5F5">$</text>
        <text x="14" y="16" font-size="14" font-weight="bold" fill="#42A5F5">€</text>
    </svg>`,
    'crypto': `<svg width="24" height="24" viewBox="0 0 24 24" fill="none">
        <circle cx="12" cy="12" r="9" stroke="#ff9800" stroke-width="2"/>
        <path d="M9 8h4c1.1 0 2 .9 2 2s-.9 2-2 2H9m4 0h1c1.1 0 2 .9 2 2s-.9 2-2 2H9" stroke="#ff9800" stroke-width="2"/>
        <line x1="12" y1="6" x2="12" y2="8" stroke="#ff9800" stroke-width="2"/>
        <line x1="12" y1="16" x2="12" y2="18" stroke="#ff9800" stroke-width="2"/>
    </svg>`,
    'gold': `<svg width="24" height="24" viewBox="0 0 24 24" fill="none">
        <circle cx="12" cy="12" r="8" fill="none" stroke="#ffd700" stroke-width="2"/>
        <circle cx="12" cy="12" r="5" fill="#ffd700"/>
    </svg>`,
    'silver': `<svg width="24" height="24" viewBox="0 0 24 24" fill="none">
        <circle cx="12" cy="12" r="8" fill="none" stroke="#c0c0c0" stroke-width="2"/>
        <circle cx="12" cy="12" r="5" fill="#c0c0c0"/>
    </svg>`,
    'oil': `<svg width="24" height="24" viewBox="0 0 24 24" fill="none">
        <path d="M8 20h8v-4h-8v4zM6 16h12v-2H6v2zM8 14h8V8c0-2.2-1.8-4-4-4S8 5.8 8 8v6z" fill="#424242"/>
    </svg>`,
    'robot': `<svg width="24" height="24" viewBox="0 0 24 24" fill="none">
        <rect x="7" y="10" width="10" height="8" rx="2" fill="#42A5F5"/>
        <circle cx="10" cy="13" r="1" fill="white"/>
        <circle cx="14" cy="13" r="1" fill="white"/>
        <rect x="9" y="15" width="6" height="1" rx="0.5" fill="white"/>
        <rect x="11" y="6" width="2" height="4" fill="#42A5F5"/>
        <circle cx="12" cy="5" r="1.5" fill="#42A5F5"/>
    </svg>`,
    'coins': `<svg width="20" height="20" viewBox="0 0 24 24" fill="white">
        <circle cx="9" cy="12" r="6" opacity="0.7"/>
        <circle cx="15" cy="12" r="6"/>
    </svg>`,
    'shield': `<svg width="20" height="20" viewBox="0 0 24 24" fill="white">
        <path d="M12,1L3,5V11C3,16.55 6.84,21.74 12,23C17.16,21.74 21,16.55 21,11V5L12,1Z"/>
    </svg>`,
    'target': `<svg width="20" height="20" viewBox="0 0 24 24" fill="white">
        <circle cx="12" cy="12" r="10" opacity="0.3"/>
        <circle cx="12" cy="12" r="6" opacity="0.6"/>
        <circle cx="12" cy="12" r="2"/>
    </svg>`,
    'rocket': `<svg width="20" height="20" viewBox="0 0 24 24" fill="white">
        <path d="M12,2A10,10 0 0,1 22,12A10,10 0 0,1 12,22A10,10 0 0,1 2,12A10,10 0 0,1 12,2M12,4A8,8 0 0,0 4,12L12,20A8,8 0 0,0 20,12L12,4Z"/>
    </svg>`
};

// ==========================================
// ESTILOS DOS BADGES
// ==========================================

const BADGE_STYLES = {
    'FREE':    'background:transparent; color:#42A5F5; border:1.5px solid #42A5F5; padding:2px 10px; border-radius:20px; font-size:11px; font-weight:700; letter-spacing:0.5px;',
    'VIP':     'background:transparent; color:#4caf50; border:1.5px solid #4caf50; padding:2px 10px; border-radius:20px; font-size:11px; font-weight:700; letter-spacing:0.5px;',
    'PREMIUM': 'background:transparent; color:#FFB300; border:1.5px solid #FFB300; padding:2px 10px; border-radius:20px; font-size:11px; font-weight:700; letter-spacing:0.5px;',
    'NOVO':    'background:#42A5F5; color:#fff; border:none; padding:2px 10px; border-radius:20px; font-size:11px; font-weight:700; letter-spacing:0.5px;',
    'TOP':     'background:#FFB300; color:#000; border:none; padding:2px 10px; border-radius:20px; font-size:11px; font-weight:700; letter-spacing:0.5px;'
};

// ==========================================
// LOAD MARKETS
// ==========================================

async function loadMarkets() {
    try {
        const response = await fetch('data/markets.json');
        const markets = await response.json();

        populateMarkets(markets.continuous, 'continuousMarkets');
        populateMarkets(markets.dailyReset, 'dailyResetMarkets');
        populateMarkets(markets.jump, 'jumpMarkets');
        populateMarkets(markets.forex, 'forexMarkets');
        populateMarkets(markets.crypto, 'cryptoMarkets');
        populateMarkets(markets.commodities, 'commodityMarkets');

        console.log('✅ Mercados carregados');
    } catch (error) {
        console.error('❌ Erro ao carregar mercados:', error);
    }
}

function populateMarkets(markets, containerId) {
    const container = document.getElementById(containerId);
    if (!container || !markets) return;

    container.innerHTML = '';

    markets.forEach(market => {
        const item = document.createElement('div');
        item.className = 'modal-list-item';
        if (market.id === 'R_100') item.classList.add('active');

        item.innerHTML = `
            <div class="item-icon">
                ${getMarketIcon(market.icon, market)}
            </div>
            <div class="item-content">
                <div class="item-name">${market.name}</div>
                ${market.description ? `<div class="item-hint">${market.description}</div>` : ''}
            </div>
            ${market.badge ? `<span class="market-badge-1s">${market.badge}</span>` : ''}
        `;

        item.onclick = () => selectMarket(market);
        container.appendChild(item);
    });
}

// Gera ícone mini-candlestick igual DC Bot
function getMarketIcon(iconName, market) {
    const num = market ? (market.number || '') : '';
    const badge1s = market && market.badge === '1s';

    // Cores por tipo
    let color = '#42A5F5';
    if (iconName && iconName.includes('jump')) color = '#ff9800';
    if (iconName === 'bear-market') color = '#f44336';
    if (iconName === 'bull-market') color = '#4caf50';
    if (iconName === 'forex') color = '#42A5F5';
    if (iconName === 'crypto') color = '#ff9800';
    if (iconName === 'gold') color = '#ffd700';
    if (iconName === 'silver') color = '#c0c0c0';
    if (iconName === 'oil') color = '#78909C';

    // Mini candlestick SVG igual DC Bot
    return `<svg width="40" height="36" viewBox="0 0 40 36">
        <text x="2" y="10" font-size="9" font-weight="700" fill="${color}" font-family="Arial">${num}</text>
        ${badge1s ? `<rect x="22" y="2" width="14" height="8" rx="2" fill="#f44336"/>
        <text x="24" y="9" font-size="6" font-weight="700" fill="white" font-family="Arial">1s</text>` : ''}
        <line x1="6" y1="14" x2="6" y2="28" stroke="${color}" stroke-width="1"/>
        <rect x="4" y="17" width="4" height="7" fill="${color}" rx="0.5"/>
        <line x1="13" y1="13" x2="13" y2="27" stroke="${color}" stroke-width="1"/>
        <rect x="11" y="16" width="4" height="8" fill="${color}" rx="0.5" opacity="0.7"/>
        <line x1="20" y1="15" x2="20" y2="30" stroke="${color}" stroke-width="1"/>
        <rect x="18" y="18" width="4" height="9" fill="${color}" rx="0.5"/>
        <line x1="27" y1="12" x2="27" y2="26" stroke="${color}" stroke-width="1"/>
        <rect x="25" y="15" width="4" height="7" fill="${color}" rx="0.5" opacity="0.7"/>
        <line x1="34" y1="16" x2="34" y2="28" stroke="${color}" stroke-width="1"/>
        <rect x="32" y="18" width="4" height="7" fill="${color}" rx="0.5"/>
    </svg>`;
}

function selectMarket(market) {
    console.log('📊 Mercado selecionado:', market.name);

    const nameEl = document.getElementById('selectedMarket');
    const hintEl = document.getElementById('marketHint');

    if (nameEl) nameEl.textContent = market.name;
    if (hintEl && market.description) hintEl.textContent = market.description;

    if (typeof window.selectMarketGlobal === 'function') {
        window.selectMarketGlobal(market);
    }

    closeMarketModal();
}

// ==========================================
// LOAD STRATEGIES — com ícones SVG do JSON e badges coloridos
// ==========================================

async function loadStrategies() {
    try {
        const response = await fetch('data/strategies.json?v=' + Date.now());
        const strategies = await response.json();

        populateStrategies(strategies.free, 'freeStrategies');
        populateStrategies(strategies.vip, 'vipStrategies');
        populateStrategies(strategies.premium, 'premiumStrategies');

        console.log('✅ Estratégias carregadas');
    } catch (error) {
        console.error('❌ Erro ao carregar estratégias:', error);
    }
}

function populateStrategies(strategies, containerId) {
    const container = document.getElementById(containerId);
    if (!container || !strategies) return;

    container.innerHTML = '';

    strategies.forEach(strategy => {
        const item = document.createElement('div');
        item.className = 'modal-list-item' + (strategy.locked ? ' locked' : '');
        if (strategy.active) item.classList.add('active');

        // Ícone: usa SVG do JSON se disponível, senão usa o robot padrão
        const iconHtml = strategy.icon && strategy.icon.startsWith('<svg')
            ? `<div style="width:36px;height:36px;display:flex;align-items:center;justify-content:center;">${strategy.icon}</div>`
            : SVG_ICONS['robot'];

        // Badges
        const badges = strategy.badges || [];
        const badgesHtml = badges.map(b =>
            `<span style="${BADGE_STYLES[b] || BADGE_STYLES['FREE']}">${b}</span>`
        ).join(' ');

        // Cadeado para travados
        const lockHtml = strategy.locked
            ? `<svg width="16" height="16" viewBox="0 0 24 24" fill="#555" style="margin-left:6px;flex-shrink:0;"><path d="M18 8h-1V6c0-2.76-2.24-5-5-5S7 3.24 7 6v2H6c-1.1 0-2 .9-2 2v10c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V10c0-1.1-.9-2-2-2zm-6 9c-1.1 0-2-.9-2-2s.9-2 2-2 2 .9 2 2-.9 2-2 2zm3.1-9H8.9V6c0-1.71 1.39-3.1 3.1-3.1 1.71 0 3.1 1.39 3.1 3.1v2z"/></svg>`
            : '';

        item.innerHTML = `
            <div style="width:36px;height:36px;display:flex;align-items:center;justify-content:center;flex-shrink:0;">
                ${strategy.icon && strategy.icon.startsWith('<svg') ? strategy.icon : SVG_ICONS['robot']}
            </div>
            <div style="flex:1;min-width:0;padding:0 10px;">
                <div style="font-size:14px;font-weight:600;color:${strategy.locked ? '#888' : '#fff'};white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">${strategy.name}</div>
            </div>
            <div style="display:flex;align-items:center;gap:6px;flex-shrink:0;">
                ${badgesHtml}
                ${lockHtml}
            </div>
        `;

        item.style.cssText = 'display:flex;align-items:center;padding:12px 16px;border-bottom:1px solid #1e2128;cursor:' + (strategy.locked ? 'not-allowed' : 'pointer') + ';transition:background 0.15s;';

        if (!strategy.locked) {
            item.onmouseenter = () => item.style.background = '#1e2128';
            item.onmouseleave = () => item.style.background = strategy.active ? '#1a2535' : '';
            item.onclick = () => selectStrategy(strategy);
        }

        if (strategy.active) item.style.background = '#1a2535';

        container.appendChild(item);
    });
}

function selectStrategy(strategy) {
    console.log('🤖 Estratégia selecionada:', strategy.name);

    const nameEl = document.getElementById('selectedStrategy');
    if (nameEl) nameEl.textContent = strategy.name;

    if (typeof window.selectStrategyGlobal === 'function') {
        window.selectStrategyGlobal(strategy);
    }

    closeStrategyModal();
}

// ==========================================
// LOAD RISK MODES
// ==========================================

async function loadRiskModes() {
    try {
        const response = await fetch('data/risk-modes.json');
        const riskModes = await response.json();

        const container = document.getElementById('riskModeList');
        if (!container) return;

        container.innerHTML = '';

        riskModes.forEach(risk => {
            const item = document.createElement('div');
            item.className = 'risk-mode-item';
            if (risk.id === 'conservative') item.classList.add('active');

            item.innerHTML = `
                <div class="risk-mode-icon" style="background: ${risk.color};">
                    ${SVG_ICONS[risk.icon] || SVG_ICONS['shield']}
                </div>
                <div class="risk-mode-content">
                    <div class="risk-mode-title">${risk.name}</div>
                    <div class="risk-mode-level" style="color: ${risk.color};">▲ ${risk.level || risk.risk_level || 'Médio risco'}</div>
                    <div class="risk-mode-min">${risk.description || `Valor recomendado: no mínimo $${risk.min_balance}`}</div>
                </div>
                ${risk.id === 'conservative' ? '<i class="fas fa-check risk-check"></i>' : ''}
            `;

            item.onclick = () => selectRiskMode(risk);
            container.appendChild(item);
        });

        console.log('✅ Modos de risco carregados');
    } catch (error) {
        console.error('❌ Erro ao carregar modos de risco:', error);
    }
}

function selectRiskMode(risk) {
    console.log('🛡️ Modo de risco selecionado:', risk.name);

    const riskButton = document.querySelector('.risk-info h6');
    const riskLevel  = document.querySelector('.risk-level span');
    const riskDesc   = document.querySelector('.risk-desc');
    const riskIcon   = document.querySelector('.risk-icon');

    if (riskButton) riskButton.textContent = risk.name;
    if (riskLevel) {
        riskLevel.textContent = risk.level || risk.risk_level || 'Médio risco';
        riskLevel.style.color = risk.color;
    }
    if (riskDesc) riskDesc.textContent = risk.description || `Valor recomendado: no mínimo $${risk.min_balance}`;
    if (riskIcon) riskIcon.style.background = risk.color;

    if (typeof window.selectRiskModeGlobal === 'function') {
        window.selectRiskModeGlobal(risk);
    }

    closeRiskModal();
}

// ==========================================
// INITIALIZE
// ==========================================

document.addEventListener('DOMContentLoaded', async () => {
    console.log('📋 Carregando dados dos modais...');
    await loadMarkets();
    await loadStrategies();
    await loadRiskModes();
    console.log('✅ Modals.js inicializado!');
});

console.log('✅ modals.js carregado!');