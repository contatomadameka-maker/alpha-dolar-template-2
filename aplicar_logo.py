#!/usr/bin/env python3
"""
ALPHA DOLAR 2.0 — Aplicar Logo + Favicon em todas as páginas
=============================================================
Execute no PythonAnywhere:
  cd /home/dirlei/alpha-dolar-2.0
  python3 aplicar_logo.py
"""

import os, re, shutil
from datetime import datetime

# Pastas a verificar
PASTAS = [
    '/home/dirlei/alpha-dolar-2.0/web',
    '/home/dirlei/alpha-dolar-2.0',
]

# Arquivos HTML a processar
ARQUIVOS = [
    '/home/dirlei/alpha-dolar-2.0/web/index.html',
    '/home/dirlei/alpha-dolar-2.0/web/dashboard-fixed.html',
    '/home/dirlei/alpha-dolar-2.0/web/login.html',
    '/home/dirlei/alpha-dolar-2.0/web/guia-digitos-alpha.html',
    '/home/dirlei/alpha-dolar-2.0/web/guia-deposito-saque.html',
    '/home/dirlei/alpha-dolar-2.0/vídeos.html',
    '/home/dirlei/alpha-dolar-2.0/videos.html',
]

# ── FAVICON INLINE ────────────────────────────────────────────
FAVICON = """<!-- ══ ALPHA DOLAR FAVICON ══ -->
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 256 256'><rect width='256' height='256' rx='52' fill='%230d1018'/%3E<rect width='256' height='256' rx='52' fill='none' stroke='%2300d2ff' stroke-width='8' stroke-opacity='0.4'/%3E<text x='32' y='195' font-family='Arial Black,sans-serif' font-weight='900' font-size='185' fill='%2300d2ff'>A</text><text x='58' y='195' font-family='Arial Black,sans-serif' font-weight='900' font-size='185' fill='none' stroke='%2300d2ff' stroke-width='8' stroke-opacity='0.4'>%24</text></svg>">
<!-- ══ FIM FAVICON ══ -->"""

# ── LOGO SVG NAVBAR ──────────────────────────────────────────
LOGO_SVG = """<svg width="160" height="36" viewBox="0 0 160 36" xmlns="http://www.w3.org/2000/svg" style="display:block">
  <defs>
    <linearGradient id="logograd" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#00d2ff"/>
      <stop offset="100%" style="stop-color:#0ea5e9"/>
    </linearGradient>
  </defs>
  <text x="0" y="32" font-family="'Arial Black',Arial,sans-serif" font-weight="900" font-size="34" fill="url(#logograd)">A</text>
  <text x="12" y="32" font-family="'Arial Black',Arial,sans-serif" font-weight="900" font-size="34" fill="none" stroke="url(#logograd)" stroke-width="1.5" opacity="0.45">$</text>
  <line x1="38" y1="4" x2="38" y2="32" stroke="#1e2230" stroke-width="1.5"/>
  <text x="46" y="20" font-family="'Arial Black',Arial,sans-serif" font-weight="900" font-size="13" fill="#e2e8f0" letter-spacing="2">ALPHA DOLAR</text>
  <text x="48" y="32" font-family="Arial,sans-serif" font-size="9" fill="#475569" letter-spacing="3">TRADING BOT 2.0</text>
</svg>"""

# Padrões de texto que serão substituídos pela logo SVG na navbar
PADROES_LOGO = [
    # Orbitron font links e spans com o nome
    r'<a[^>]*class=["\'][^"\']*nav-logo[^"\']*["\'][^>]*>.*?</a>',
    r'<span[^>]*class=["\'][^"\']*nav-logo[^"\']*["\'][^>]*>.*?</span>',
    r'<div[^>]*class=["\'][^"\']*nav-logo[^"\']*["\'][^>]*>.*?</div>',
    # Texto simples na navbar
    r'ALPHA <span[^>]*>Dolar</span> 2\.0',
    r'Alpha <span[^>]*>Dolar</span> 2\.0',
    r'ALPHA DOLAR 2\.0',
]

ts = datetime.now().strftime('%Y%m%d_%H%M%S')
ok_favicon = 0
ok_logo = 0
skip = 0

print("=" * 60)
print("ALPHA DOLAR 2.0 — Aplicar Logo + Favicon")
print("=" * 60)

for caminho in ARQUIVOS:
    if not os.path.exists(caminho):
        print(f"⚠️  {os.path.basename(caminho)} — não encontrado, pulando")
        skip += 1
        continue

    with open(caminho, 'r', encoding='utf-8') as f:
        html = f.read()

    alterado = False
    backup_feito = False

    # ── 1. FAVICON ─────────────────────────────────────────
    if 'ALPHA DOLAR FAVICON' not in html:
        if not backup_feito:
            shutil.copy2(caminho, caminho + f'.bak_{ts}')
            backup_feito = True
        html = html.replace('</head>', FAVICON + '\n</head>', 1)
        alterado = True
        ok_favicon += 1
        print(f"🌟  {os.path.basename(caminho)} — favicon aplicado")
    else:
        print(f"✅  {os.path.basename(caminho)} — favicon já existe")

    # ── 2. LOGO NA NAVBAR ──────────────────────────────────
    logo_aplicada = False
    for padrao in PADROES_LOGO:
        match = re.search(padrao, html, re.DOTALL | re.IGNORECASE)
        if match:
            if not backup_feito:
                shutil.copy2(caminho, caminho + f'.bak_{ts}')
                backup_feito = True
            html = html[:match.start()] + LOGO_SVG + html[match.end():]
            alterado = True
            logo_aplicada = True
            ok_logo += 1
            print(f"🎨  {os.path.basename(caminho)} — logo SVG aplicada")
            break

    if not logo_aplicada:
        print(f"ℹ️   {os.path.basename(caminho)} — logo: padrão não encontrado (ok se não tem navbar)")

    # ── SALVA ──────────────────────────────────────────────
    if alterado:
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(html)

print()
print(f"🌟  Favicons:  {ok_favicon}")
print(f"🎨  Logos:     {ok_logo}")
print(f"⏭️  Pulados:   {skip}")
print()
print("Recarregue o PythonAnywhere para ver as mudanças!")
print("Para desfazer: restaure os arquivos .bak_" + ts)