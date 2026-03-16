import shutil, sys

HTML = "/home/dirlei/alpha-dolar-2.0/web/dashboard-fixed.html"
shutil.copy2(HTML, HTML + ".backup")
print("✅ Backup criado")

html = open(HTML, encoding="utf-8").read()
count = 0

fixes = [
    (
        "position: fixed;\n            bottom: 20px;\n            left: 20px;\n            width: auto;\n            height: auto;\n            background: transparent;\n            backdrop-filter: none;\n            display: none;\n            z-index: 99999;\n            pointer-events: none;",
        "position: fixed;\n            top: 0; left: 0; right: 0; bottom: 0;\n            width: 100%;\n            height: 100%;\n            background: rgba(0,0,0,0.78);\n            backdrop-filter: blur(2px);\n            display: none;\n            align-items: center;\n            justify-content: center;\n            z-index: 99999;\n            pointer-events: auto;\n            padding: 20px;\n            box-sizing: border-box;"
    ),
    (
        "background: var(--brand-color-panel);\n            border-radius: 16px;\n            width: 340px;\n            box-shadow: 0 10px 30px rgba(0,0,0,0.5);\n            border: 1px solid var(--brand-color-border);\n            overflow: hidden;\n            padding: 0;",
        "background: #1e2128;\n            border-radius: 16px;\n            width: 100%;\n            max-width: 420px;\n            max-height: calc(100vh - 60px);\n            overflow-y: auto;\n            overflow-x: hidden;\n            box-shadow: 0 20px 60px rgba(0,0,0,0.6);\n            border: 1px solid #2a2d35;\n            padding: 0;"
    ),
    (
        "alert('⚠️ O bot já está em execução.');",
        "console.warn('Bot já rodando');"
    ),
]

for old, new in fixes:
    if old in html:
        html = html.replace(old, new, 1)
        count += 1
        print(f"✅ Fix {count} aplicado")
    else:
        print(f"⚠️  Trecho não encontrado (já aplicado?)")

open(HTML, "w", encoding="utf-8").write(html)
print(f"\n✅ Pronto! {count} fixes aplicados.")
