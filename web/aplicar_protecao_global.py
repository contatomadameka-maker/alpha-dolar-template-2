#!/usr/bin/env python3
"""
ALPHA DOLAR 2.0 — Proteção Global de Acesso
============================================
Aplica verificação de login Deriv em TODAS as páginas.
Quem não tiver token salvo (não fez login) é redirecionado para /login.

Execute no PythonAnywhere:
  cd /home/dirlei/alpha-dolar-2.0/web
  python3 aplicar_protecao_global.py
"""

import os, shutil
from datetime import datetime

WEB_DIR  = '/home/dirlei/alpha-dolar-2.0/web'
LOGIN_URL = '/login'

# Páginas que precisam de proteção (qualquer um que não seja o login)
PROTEGER = [
    'index.html',           # /home
    'dashboard-fixed.html', # /dashboard
    'videos.html',          # /videos
    'guia-digitos-alpha.html',
    'guia-deposito-saque.html',
]

# Páginas que NÃO devem ser protegidas (o próprio login)
IGNORAR = ['login.html']

# ── O guard que será inserido em cada página ─────────────────
GUARD = """
<!-- ══ ALPHA GUARD ══ -->
<script>
(function(){
  try {
    var raw = localStorage.getItem('deriv_accounts');
    if (!raw) throw 'sem_token';
    var contas = JSON.parse(raw);
    if (!contas || contas.length === 0) throw 'sem_contas';
    // Verifica se pelo menos um token existe
    var temToken = contas.some(function(c){ return c.token && c.token.length > 5; });
    if (!temToken) throw 'token_invalido';
    // Tudo OK — usuário autenticado
  } catch(e) {
    // Sem login válido — redireciona para login
    window.location.replace('""" + LOGIN_URL + """');
  }
})();
</script>
<!-- ══ FIM ALPHA GUARD ══ -->
"""

ts = datetime.now().strftime('%Y%m%d_%H%M%S')
ok = 0
skip = 0
erros = 0

print("=" * 60)
print("ALPHA DOLAR 2.0 — Proteção Global de Acesso")
print("=" * 60)

for nome in PROTEGER:
    caminho = os.path.join(WEB_DIR, nome)

    if not os.path.exists(caminho):
        print(f"⚠️  {nome} — não encontrado, pulando")
        skip += 1
        continue

    with open(caminho, 'r', encoding='utf-8') as f:
        html = f.read()

    # Já tem o guard? Pula
    if 'ALPHA GUARD' in html:
        print(f"✅  {nome} — já protegido")
        skip += 1
        continue

    # Backup
    backup = caminho + f'.bak_{ts}'
    shutil.copy2(caminho, backup)

    # Insere o guard logo após o <head> — antes de qualquer CSS/JS carregar
    if '<head>' in html:
        html = html.replace('<head>', '<head>' + GUARD, 1)
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"🔒  {nome} — proteção aplicada ✓")
        ok += 1
    else:
        print(f"❌  {nome} — tag <head> não encontrada")
        erros += 1

print()
print(f"✅  Protegidos:  {ok}")
print(f"⏭️  Pulados:     {skip}")
print(f"❌  Erros:       {erros}")
print()
print("Como funciona agora:")
print("  • Qualquer página → verifica localStorage por token Deriv")
print("  • Sem token → redireciona para /login automaticamente")
print("  • Com token → acesso liberado normalmente")
print("  • Login.html → nunca é bloqueado")
print()
print("Para DESFAZER, restaure os arquivos .bak_" + ts)