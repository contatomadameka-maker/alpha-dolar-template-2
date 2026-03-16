#!/usr/bin/env python3
"""
Corrige navbar do dashboard para mobile
Esconde botões secundários em telas pequenas, mantém Início + Operar sempre visíveis
"""

ARQUIVO = '/home/dirlei/alpha-dolar-2.0/web/dashboard-fixed.html'

CSS_MOBILE = """
/* ── Navbar mobile fix ── */
@media (max-width: 600px) {
  #homeNavBar { padding: 0 8px !important; }
  #homeNavBar .nav-hide-mobile { display: none !important; }
  #homeNavBar .nav-right-icons { display: none !important; }
}
"""

with open(ARQUIVO, 'r', encoding='utf-8') as f:
    html = f.read()

if 'nav-hide-mobile' in html:
    print("✅ Já corrigido!")
    exit(0)

# 1. Injeta CSS
html = html.replace('</style>', CSS_MOBILE + '\n</style>', 1)

# 2. Marca botões secundários com classe nav-hide-mobile
# AI Signals, Loja, Vídeos, Suporte ficam ocultos no mobile
for texto in ['✦ AI Signals', '🛒 Loja', '📺 Vídeos', '💬 Suporte']:
    # Adiciona classe no button/a que contém esse texto
    html = html.replace(
        f'>{texto}</button>',
        f' class="nav-hide-mobile">{texto}</button>'
    )
    html = html.replace(
        f'>{texto}</a>',
        f' class="nav-hide-mobile">{texto}</a>'
    )

# 3. Marca div dos ícones direita com nav-right-icons
html = html.replace(
    '<a href="https://instagram.com"',
    '<div class="nav-right-icons" style="display:flex;align-items:center;gap:6px"><a href="https://instagram.com"',
    1
)
# Fecha a div antes do fechamento da navbar
html = html.replace(
    '</a>    </div>    </div>',
    '</a></div>    </div>',
    1
)

with open(ARQUIVO, 'w', encoding='utf-8') as f:
    f.write(html)

print("✅ Navbar mobile corrigida!")
print("   Mobile: mostra apenas 🏠 Início + ⚡ Operar")
print("   Desktop: mostra tudo normalmente")