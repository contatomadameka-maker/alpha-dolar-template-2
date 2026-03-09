#!/usr/bin/env python3
import shutil
from datetime import datetime

ARQUIVO = '/home/dirlei/alpha-dolar-2.0/vídeos.html'

# Tenta também sem acento caso o nome seja diferente
import os
if not os.path.exists(ARQUIVO):
    ARQUIVO = '/home/dirlei/alpha-dolar-2.0/videos.html'

if not os.path.exists(ARQUIVO):
    print("❌ videos.html não encontrado. Verifique o nome exato do arquivo.")
    exit(1)

print(f"📄 Arquivo: {ARQUIVO}")

with open(ARQUIVO, 'r', encoding='utf-8') as f:
    html = f.read()

if 'ALPHA GUARD' in html:
    print("✅ Já estava protegido — nada a fazer.")
    exit(0)

# Backup
ts = datetime.now().strftime('%Y%m%d_%H%M%S')
shutil.copy2(ARQUIVO, ARQUIVO + f'.bak_{ts}')

GUARD = """<!-- ══ ALPHA GUARD ══ -->
<script>
(function(){
  try {
    var raw = localStorage.getItem('deriv_accounts');
    if (!raw) throw 'sem_token';
    var contas = JSON.parse(raw);
    if (!contas || contas.length === 0) throw 'sem_contas';
    var temToken = contas.some(function(c){ return c.token && c.token.length > 5; });
    if (!temToken) throw 'token_invalido';
  } catch(e) {
    window.location.replace('/login');
  }
})();
</script>
<!-- ══ FIM ALPHA GUARD ══ -->"""

html = html.replace('<head>', '<head>\n' + GUARD, 1)

with open(ARQUIVO, 'w', encoding='utf-8') as f:
    f.write(html)

print("🔒 videos.html — proteção aplicada ✓")