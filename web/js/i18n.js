/**
 * ALPHA DOLAR 2.0 — Sistema de Internacionalização (i18n)
 * Suporta: PT, EN, ES, HI, ID, TH, VI, AR, IT, FR, DE
 * Não modifica o HTML — aplica traduções via JS por cima
 */

(function() {
'use strict';

const TRANSLATIONS = {

  pt: {}, // Português é o padrão — sem tradução necessária

  en: {
    // ── Navegação / Menu ──
    'Início': 'Home',
    'Operar': 'Trade',
    'Alpha Signals': 'Alpha Signals',
    'Loja': 'Store',
    'Tutoriais/Vídeos': 'Tutorials/Videos',
    'Analytics': 'Analytics',
    'Suporte': 'Support',
    'Entrar no Canal': 'Join Channel',

    // ── Conta ──
    'Conta Demo': 'Demo Account',
    'Conta Real': 'Real Account',
    'Sair da conta': 'Sign out',
    'Perfil': 'Profile',
    'Sons: Ligado': 'Sound: On',
    'Sons: Desligado': 'Sound: Off',
    'IDIOMA': 'LANGUAGE',
    'CONTA': 'ACCOUNT',

    // ── Bot / Operações ──
    'Iniciar Robô': 'Start Bot',
    'Parar Robô': 'Stop Bot',
    'Iniciando...': 'Starting...',
    'Parando...': 'Stopping...',
    'Aguardando sinal...': 'Waiting for signal...',
    'Buscando sinal...': 'Searching for signal...',
    'Analisando Mercado.': 'Analyzing Market.',
    'Análise Finalizada': 'Analysis Complete',
    'Preparando para comprar contrato': 'Preparing to buy contract',
    'Iniciando uma nova sessão': 'Starting a new session',
    'Começando a análise': 'Starting analysis',
    'Negociação finalizada': 'Trade completed',
    'Tempo executando a estratégia': 'Time running strategy',
    'Conexão perdida — clique em Iniciar para reconectar': 'Connection lost — click Start to reconnect',

    // ── Painel Esquerdo ──
    'Quantia inicial': 'Initial Amount',
    'Lucro alvo': 'Target Profit',
    'Limite de perda': 'Stop Loss',
    'Mercado': 'Market',
    'Estratégia': 'Strategy',
    'Modo': 'Mode',
    'Gerenciamento de risco': 'Risk Management',
    'Modo de negociação': 'Trading Mode',
    'MODO DE NEGOCIAÇÃO': 'TRADING MODE',
    'GERENCIAMENTO DE RISCO': 'RISK MANAGEMENT',
    'MERCADO': 'MARKET',
    'ESTRATÉGIA': 'STRATEGY',
    'MODO': 'MODE',

    // ── Modos ──
    'Veloz': 'Fast',
    'Mais negociações, menos precisão': 'More trades, less precision',
    'Preciso': 'Precise',
    'Menos negociações, mais precisão': 'Fewer trades, more precision',
    'Equilibrado': 'Balanced',
    'Conservador': 'Conservative',
    'Baixo risco': 'Low risk',
    'Agressivo': 'Aggressive',
    'Alto risco': 'High risk',
    'Valor recomendado: no mínimo $50': 'Recommended: minimum $50',

    // ── Abas do painel direito ──
    'GRÁFICO': 'CHART',
    'DÍGITOS': 'DIGITS',
    'NEGOCIAÇÕES': 'TRADES',
    'REGISTROS': 'LOGS',
    'LOG EM TEMPO REAL': 'REAL-TIME LOG',
    'Limpar': 'Clear',

    // ── Resultados ──
    'Ganho': 'Win',
    'Perda': 'Loss',
    'WIN': 'WIN',
    'LOSS': 'LOSS',
    'Próx. stake:': 'Next stake:',
    'Win Rate:': 'Win Rate:',
    'Trades:': 'Trades:',
    'Step inicial': 'Initial step',
    'Martingale': 'Martingale',

    // ── Ferramentas Alpha ──
    'FERRAMENTAS ALPHA': 'ALPHA TOOLS',
    'Alpha Shield': 'Alpha Shield',
    'PROTEÇÃO': 'PROTECTION',
    'Alpha Pattern': 'Alpha Pattern',
    'PADRÕES': 'PATTERNS',
    'Alpha Clock': 'Alpha Clock',
    'HORÁRIOS': 'SCHEDULES',
    'Alpha Bank': 'Alpha Bank',
    'SMART': 'SMART',

    // ── Modal Bot Parado ──
    'Sessão Encerrada': 'Session Ended',
    'Total de trades': 'Total trades',
    'Vitórias': 'Wins',
    'Derrotas': 'Losses',
    'Lucro total': 'Total profit',
    'Win rate': 'Win rate',
    'Saldo atual': 'Current balance',
    'Motivo': 'Reason',
    'Lucro alvo atingido': 'Target profit reached',
    'Stop loss atingido': 'Stop loss reached',
    'Parado manualmente': 'Manually stopped',
    'Nova Sessão': 'New Session',
    'Continuar': 'Continue',

    // ── Modo Manual ──
    'Modo manual': 'Manual mode',
    'Agendar': 'Schedule',
    'TIPO DE NEGOCIAÇÃO': 'CONTRACT TYPE',
    'DURAÇÃO': 'DURATION',
    'QUANTIA INICIAL': 'INITIAL AMOUNT',
    'Multiplicador de entrada': 'Entry multiplier',
    'Rise Equal': 'Rise Equal',
    'Fall Equal': 'Fall Equal',
    'Total Trades:': 'Total Trades:',
    'Tiques': 'Ticks',
    'segundos': 'seconds',
    'minutos': 'minutes',

    // ── IA PRO ──
    'Alpha IA Pro': 'Alpha AI Pro',
    'PREMIUM': 'PREMIUM',
    'Conectar': 'Connect',
    'Desconectar': 'Disconnect',
    'Coletando dados...': 'Collecting data...',
    'Conectado!': 'Connected!',

    // ── Notificações ──
    'Bot iniciado com sucesso': 'Bot started successfully',
    'Bot parado': 'Bot stopped',
    'Erro ao iniciar bot': 'Error starting bot',

    // ── Topbar ──
    'Lucro total da sessão': 'Total session profit',
    'do saldo': 'of balance',
  },

  es: {
    'Início': 'Inicio',
    'Operar': 'Operar',
    'Loja': 'Tienda',
    'Tutoriais/Vídeos': 'Tutoriales/Videos',
    'Suporte': 'Soporte',
    'Entrar no Canal': 'Entrar al Canal',
    'Conta Demo': 'Cuenta Demo',
    'Conta Real': 'Cuenta Real',
    'Sair da conta': 'Cerrar sesión',
    'Perfil': 'Perfil',
    'Sons: Ligado': 'Sonido: Activado',
    'Sons: Desligado': 'Sonido: Desactivado',
    'IDIOMA': 'IDIOMA',
    'CONTA': 'CUENTA',
    'Iniciar Robô': 'Iniciar Robot',
    'Parar Robô': 'Detener Robot',
    'Aguardando sinal...': 'Esperando señal...',
    'Buscando sinal...': 'Buscando señal...',
    'Analisando Mercado.': 'Analizando Mercado.',
    'Análise Finalizada': 'Análisis Finalizado',
    'Quantia inicial': 'Cantidad inicial',
    'Lucro alvo': 'Ganancia objetivo',
    'Limite de perda': 'Límite de pérdida',
    'Mercado': 'Mercado',
    'Estratégia': 'Estrategia',
    'Modo': 'Modo',
    'Gerenciamento de risco': 'Gestión de riesgo',
    'GRÁFICO': 'GRÁFICO',
    'DÍGITOS': 'DÍGITOS',
    'NEGOCIAÇÕES': 'OPERACIONES',
    'REGISTROS': 'REGISTROS',
    'LOG EM TEMPO REAL': 'REGISTRO EN TIEMPO REAL',
    'Limpar': 'Limpiar',
    'Ganho': 'Ganancia',
    'Perda': 'Pérdida',
    'Veloz': 'Rápido',
    'Preciso': 'Preciso',
    'Conservador': 'Conservador',
    'Agressivo': 'Agresivo',
    'PROTEÇÃO': 'PROTECCIÓN',
    'PADRÕES': 'PATRONES',
    'HORÁRIOS': 'HORARIOS',
    'Sessão Encerrada': 'Sesión Terminada',
    'Total de trades': 'Total de operaciones',
    'Vitórias': 'Victorias',
    'Derrotas': 'Derrotas',
    'Lucro total': 'Ganancia total',
    'Saldo atual': 'Saldo actual',
    'Nova Sessão': 'Nueva Sesión',
    'Modo manual': 'Modo manual',
    'Tiques': 'Ticks',
    'DURAÇÃO': 'DURACIÓN',
    'QUANTIA INICIAL': 'CANTIDAD INICIAL',
    'Multiplicador de entrada': 'Multiplicador de entrada',
  },

  hi: {
    'Início': 'होम',
    'Operar': 'ट्रेड',
    'Loja': 'स्टोर',
    'Tutoriais/Vídeos': 'ट्यूटोरियल/वीडियो',
    'Suporte': 'सहायता',
    'Conta Demo': 'डेमो खाता',
    'Conta Real': 'वास्तविक खाता',
    'Sair da conta': 'लॉग आउट',
    'Iniciar Robô': 'बॉट शुरू करें',
    'Parar Robô': 'बॉट रोकें',
    'Aguardando sinal...': 'संकेत की प्रतीक्षा...',
    'Quantia inicial': 'प्रारंभिक राशि',
    'Lucro alvo': 'लक्ष्य लाभ',
    'Limite de perda': 'हानि सीमा',
    'Mercado': 'बाजार',
    'Estratégia': 'रणनीति',
    'GRÁFICO': 'चार्ट',
    'NEGOCIAÇÕES': 'ट्रेड',
    'REGISTROS': 'लॉग',
    'Limpar': 'साफ करें',
    'Ganho': 'जीत',
    'Perda': 'हार',
    'Conservador': 'रूढ़िवादी',
    'Nova Sessão': 'नया सत्र',
    'Modo manual': 'मैनुअल मोड',
  },

  id: {
    'Início': 'Beranda',
    'Operar': 'Trading',
    'Loja': 'Toko',
    'Tutoriais/Vídeos': 'Tutorial/Video',
    'Suporte': 'Dukungan',
    'Conta Demo': 'Akun Demo',
    'Conta Real': 'Akun Nyata',
    'Sair da conta': 'Keluar',
    'Iniciar Robô': 'Mulai Bot',
    'Parar Robô': 'Hentikan Bot',
    'Aguardando sinal...': 'Menunggu sinyal...',
    'Buscando sinal...': 'Mencari sinyal...',
    'Analisando Mercado.': 'Menganalisis Pasar.',
    'Quantia inicial': 'Jumlah awal',
    'Lucro alvo': 'Target profit',
    'Limite de perda': 'Batas kerugian',
    'Mercado': 'Pasar',
    'Estratégia': 'Strategi',
    'GRÁFICO': 'GRAFIK',
    'NEGOCIAÇÕES': 'PERDAGANGAN',
    'REGISTROS': 'LOG',
    'Limpar': 'Bersihkan',
    'Ganho': 'Menang',
    'Perda': 'Kalah',
    'Conservador': 'Konservatif',
    'Veloz': 'Cepat',
    'Nova Sessão': 'Sesi Baru',
    'Modo manual': 'Mode manual',
    'Tiques': 'Tik',
  },

  th: {
    'Início': 'หน้าแรก',
    'Operar': 'เทรด',
    'Loja': 'ร้านค้า',
    'Tutoriais/Vídeos': 'บทเรียน/วิดีโอ',
    'Suporte': 'ฝ่ายสนับสนุน',
    'Conta Demo': 'บัญชีทดลอง',
    'Conta Real': 'บัญชีจริง',
    'Sair da conta': 'ออกจากระบบ',
    'Iniciar Robô': 'เริ่มบอต',
    'Parar Robô': 'หยุดบอต',
    'Aguardando sinal...': 'รอสัญญาณ...',
    'Quantia inicial': 'จำนวนเริ่มต้น',
    'Lucro alvo': 'เป้าหมายกำไร',
    'Limite de perda': 'จำกัดการสูญเสีย',
    'Mercado': 'ตลาด',
    'Estratégia': 'กลยุทธ์',
    'GRÁFICO': 'กราฟ',
    'NEGOCIAÇÕES': 'การเทรด',
    'REGISTROS': 'บันทึก',
    'Limpar': 'ล้าง',
    'Ganho': 'ชนะ',
    'Perda': 'แพ้',
    'Conservador': 'อนุรักษ์นิยม',
    'Nova Sessão': 'เซสชั่นใหม่',
    'Modo manual': 'โหมดแมนนวล',
  },

  vi: {
    'Início': 'Trang chủ',
    'Operar': 'Giao dịch',
    'Loja': 'Cửa hàng',
    'Tutoriais/Vídeos': 'Hướng dẫn/Video',
    'Suporte': 'Hỗ trợ',
    'Conta Demo': 'Tài khoản Demo',
    'Conta Real': 'Tài khoản Thật',
    'Sair da conta': 'Đăng xuất',
    'Iniciar Robô': 'Khởi động Bot',
    'Parar Robô': 'Dừng Bot',
    'Aguardando sinal...': 'Đang chờ tín hiệu...',
    'Buscando sinal...': 'Đang tìm tín hiệu...',
    'Analisando Mercado.': 'Đang phân tích thị trường.',
    'Quantia inicial': 'Số tiền ban đầu',
    'Lucro alvo': 'Mục tiêu lợi nhuận',
    'Limite de perda': 'Giới hạn thua lỗ',
    'Mercado': 'Thị trường',
    'Estratégia': 'Chiến lược',
    'GRÁFICO': 'BIỂU ĐỒ',
    'NEGOCIAÇÕES': 'GIAO DỊCH',
    'REGISTROS': 'NHẬT KÝ',
    'Limpar': 'Xóa',
    'Ganho': 'Thắng',
    'Perda': 'Thua',
    'Conservador': 'Thận trọng',
    'Veloz': 'Nhanh',
    'Nova Sessão': 'Phiên mới',
    'Modo manual': 'Chế độ thủ công',
    'Tiques': 'Tích tắc',
  },

  ar: {
    'Início': 'الرئيسية',
    'Operar': 'تداول',
    'Loja': 'المتجر',
    'Tutoriais/Vídeos': 'دروس/فيديوهات',
    'Suporte': 'الدعم',
    'Conta Demo': 'حساب تجريبي',
    'Conta Real': 'حساب حقيقي',
    'Sair da conta': 'تسجيل الخروج',
    'Iniciar Robô': 'تشغيل البوت',
    'Parar Robô': 'إيقاف البوت',
    'Aguardando sinal...': 'في انتظار الإشارة...',
    'Buscando sinal...': 'جارٍ البحث عن إشارة...',
    'Analisando Mercado.': 'تحليل السوق.',
    'Quantia inicial': 'المبلغ الأولي',
    'Lucro alvo': 'الربح المستهدف',
    'Limite de perda': 'حد الخسارة',
    'Mercado': 'السوق',
    'Estratégia': 'الاستراتيجية',
    'GRÁFICO': 'الرسم البياني',
    'NEGOCIAÇÕES': 'الصفقات',
    'REGISTROS': 'السجلات',
    'Limpar': 'مسح',
    'Ganho': 'ربح',
    'Perda': 'خسارة',
    'Conservador': 'محافظ',
    'Veloz': 'سريع',
    'Nova Sessão': 'جلسة جديدة',
    'Modo manual': 'الوضع اليدوي',
    'Tiques': 'نقرات',
  },

  it: {
    'Início': 'Home',
    'Operar': 'Trading',
    'Loja': 'Negozio',
    'Tutoriais/Vídeos': 'Tutorial/Video',
    'Suporte': 'Supporto',
    'Conta Demo': 'Conto Demo',
    'Conta Real': 'Conto Reale',
    'Sair da conta': 'Disconnetti',
    'Iniciar Robô': 'Avvia Bot',
    'Parar Robô': 'Ferma Bot',
    'Aguardando sinal...': 'In attesa di segnale...',
    'Buscando sinal...': 'Ricerca segnale...',
    'Analisando Mercado.': 'Analisi del mercato.',
    'Análise Finalizada': 'Analisi completata',
    'Quantia inicial': 'Importo iniziale',
    'Lucro alvo': 'Profitto target',
    'Limite de perda': 'Stop loss',
    'Mercado': 'Mercato',
    'Estratégia': 'Strategia',
    'GRÁFICO': 'GRAFICO',
    'NEGOCIAÇÕES': 'OPERAZIONI',
    'REGISTROS': 'REGISTRO',
    'Limpar': 'Cancella',
    'Ganho': 'Vittoria',
    'Perda': 'Perdita',
    'Conservador': 'Conservativo',
    'Veloz': 'Veloce',
    'Preciso': 'Preciso',
    'Nova Sessão': 'Nuova Sessione',
    'Modo manual': 'Modalità manuale',
    'Tiques': 'Tick',
    'PROTEÇÃO': 'PROTEZIONE',
    'PADRÕES': 'MODELLI',
    'HORÁRIOS': 'ORARI',
  },

  fr: {
    'Início': 'Accueil',
    'Operar': 'Trading',
    'Loja': 'Boutique',
    'Tutoriais/Vídeos': 'Tutoriels/Vidéos',
    'Suporte': 'Support',
    'Conta Demo': 'Compte Démo',
    'Conta Real': 'Compte Réel',
    'Sair da conta': 'Se déconnecter',
    'Iniciar Robô': 'Démarrer le Bot',
    'Parar Robô': 'Arrêter le Bot',
    'Aguardando sinal...': 'En attente du signal...',
    'Buscando sinal...': 'Recherche de signal...',
    'Analisando Mercado.': 'Analyse du marché.',
    'Análise Finalizada': 'Analyse terminée',
    'Quantia inicial': 'Montant initial',
    'Lucro alvo': 'Profit cible',
    'Limite de perda': 'Limite de perte',
    'Mercado': 'Marché',
    'Estratégia': 'Stratégie',
    'GRÁFICO': 'GRAPHIQUE',
    'NEGOCIAÇÕES': 'TRANSACTIONS',
    'REGISTROS': 'JOURNAUX',
    'Limpar': 'Effacer',
    'Ganho': 'Gain',
    'Perda': 'Perte',
    'Conservador': 'Conservateur',
    'Veloz': 'Rapide',
    'Preciso': 'Précis',
    'Nova Sessão': 'Nouvelle Session',
    'Modo manual': 'Mode manuel',
    'Tiques': 'Ticks',
    'PROTEÇÃO': 'PROTECTION',
    'PADRÕES': 'MODÈLES',
    'HORÁRIOS': 'HORAIRES',
  },

  de: {
    'Início': 'Startseite',
    'Operar': 'Handeln',
    'Loja': 'Shop',
    'Tutoriais/Vídeos': 'Tutorials/Videos',
    'Suporte': 'Support',
    'Conta Demo': 'Demo-Konto',
    'Conta Real': 'Echtes Konto',
    'Sair da conta': 'Abmelden',
    'Iniciar Robô': 'Bot starten',
    'Parar Robô': 'Bot stoppen',
    'Aguardando sinal...': 'Warte auf Signal...',
    'Buscando sinal...': 'Signal wird gesucht...',
    'Analisando Mercado.': 'Markt wird analysiert.',
    'Análise Finalizada': 'Analyse abgeschlossen',
    'Quantia inicial': 'Anfangsbetrag',
    'Lucro alvo': 'Gewinnziel',
    'Limite de perda': 'Verlustlimit',
    'Mercado': 'Markt',
    'Estratégia': 'Strategie',
    'GRÁFICO': 'DIAGRAMM',
    'NEGOCIAÇÕES': 'HANDEL',
    'REGISTROS': 'PROTOKOLL',
    'Limpar': 'Löschen',
    'Ganho': 'Gewinn',
    'Perda': 'Verlust',
    'Conservador': 'Konservativ',
    'Veloz': 'Schnell',
    'Preciso': 'Präzise',
    'Nova Sessão': 'Neue Sitzung',
    'Modo manual': 'Manueller Modus',
    'Tiques': 'Ticks',
    'PROTEÇÃO': 'SCHUTZ',
    'PADRÕES': 'MUSTER',
    'HORÁRIOS': 'ZEITPLÄNE',
  }
};

// ── Direções RTL ──
const RTL_LANGS = ['ar'];

// ── Estado atual ──
let _currentLang = localStorage.getItem('alpha_lang') || 'pt';
let _observer = null;

// ── Traduz um texto ──
function t(text) {
  if (!text || !text.trim()) return text;
  const dict = TRANSLATIONS[_currentLang];
  if (!dict) return text;
  return dict[text.trim()] || text;
}

// ── Traduz um nó de texto ──
function traduzirNo(node) {
  if (node.nodeType !== Node.TEXT_NODE) return;
  const original = node._i18nOriginal || node.textContent;
  const trimmed  = original.trim();
  if (!trimmed) return;
  const traduzido = t(trimmed);
  if (traduzido !== trimmed) {
    node._i18nOriginal = original;
    node.textContent   = original.replace(trimmed, traduzido);
  } else if (node._i18nOriginal) {
    // Restaura original se voltar para PT
    node.textContent   = node._i18nOriginal;
    node._i18nOriginal = null;
  }
}

// ── Traduz atributos (placeholder, title, aria-label) ──
function traduzirAtributos(el) {
  ['placeholder', 'title', 'aria-label'].forEach(attr => {
    const val = el.getAttribute(attr);
    if (!val) return;
    const orig = el._i18nAttrs?.[attr] || val;
    const tr   = t(orig);
    if (!el._i18nAttrs) el._i18nAttrs = {};
    el._i18nAttrs[attr] = orig;
    if (tr !== orig) el.setAttribute(attr, tr);
    else el.setAttribute(attr, orig);
  });
}

// ── Percorre o DOM e traduz ──
function traduzirDOM(root) {
  root = root || document.body;
  const walker = document.createTreeWalker(
    root,
    NodeFilter.SHOW_TEXT | NodeFilter.SHOW_ELEMENT,
    {
      acceptNode(node) {
        // Ignora scripts, styles e elementos invisíveis
        if (node.nodeType === Node.ELEMENT_NODE) {
          const tag = node.tagName?.toLowerCase();
          if (['script','style','noscript'].includes(tag)) return NodeFilter.FILTER_REJECT;
          traduzirAtributos(node);
          return NodeFilter.FILTER_SKIP;
        }
        return NodeFilter.FILTER_ACCEPT;
      }
    }
  );
  let node;
  while ((node = walker.nextNode())) {
    traduzirNo(node);
  }
}

// ── Aplica direção RTL/LTR ──
function aplicarDirecao(lang) {
  const dir = RTL_LANGS.includes(lang) ? 'rtl' : 'ltr';
  document.documentElement.setAttribute('dir', dir);
  document.documentElement.setAttribute('lang', lang);
}

// ── Troca de idioma ──
function aplicarIdioma(lang) {
  if (!TRANSLATIONS[lang] && lang !== 'pt') {
    console.warn('[i18n] Idioma não suportado:', lang);
    return;
  }
  _currentLang = lang;
  localStorage.setItem('alpha_lang', lang);
  aplicarDirecao(lang);
  traduzirDOM(document.body);

  // Observa mudanças futuras no DOM
  if (_observer) _observer.disconnect();
  _observer = new MutationObserver(function(mutations) {
    mutations.forEach(function(mutation) {
      mutation.addedNodes.forEach(function(node) {
        if (node.nodeType === Node.ELEMENT_NODE) {
          traduzirDOM(node);
        } else if (node.nodeType === Node.TEXT_NODE) {
          traduzirNo(node);
        }
      });
    });
  });
  _observer.observe(document.body, {
    childList: true,
    subtree: true,
    characterData: false
  });
}

// ── API pública ──
window.i18n = {
  apply:   aplicarIdioma,
  t:       t,
  getLang: () => _currentLang,
  addTranslations: function(lang, dict) {
    if (!TRANSLATIONS[lang]) TRANSLATIONS[lang] = {};
    Object.assign(TRANSLATIONS[lang], dict);
  }
};

// ── Hook no trocarIdioma existente ──
const _origTrocarIdioma = window.trocarIdioma;
window.trocarIdioma = function(lang, el) {
  if (_origTrocarIdioma) _origTrocarIdioma(lang, el);
  aplicarIdioma(lang);
};

// ── Auto-aplica ao carregar ──
function init() {
  const savedLang = localStorage.getItem('alpha_lang') || 'pt';
  if (savedLang && savedLang !== 'pt') {
    aplicarIdioma(savedLang);
  } else {
    aplicarDirecao('pt');
  }
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  // DOM já carregado — aplica com pequeno delay para o dashboard renderizar
  setTimeout(init, 500);
}

})();