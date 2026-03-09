import shutil
HTML = "/home/dirlei/alpha-dolar-2.0/web/dashboard-fixed.html"
shutil.copy2(HTML, HTML + ".backup3")
html = open(HTML, encoding="utf-8").read()
count = 0
fixes = [
    (
        '            top: 56px;\n            left: 0;\n            width: var(--left-panel-width, 340px);\n            height: calc(100vh - 56px);',
        '            top: 0;\n            left: 0;\n            width: var(--left-panel-width, 340px);\n            height: 100vh;'
    ),
    (
        '            width: 340px;\n            height: 100%;',
        '            width: 100%;\n            height: 100%;'
    ),
    (
        '            font-size: 26px !important;\n            font-weight: 700 !important;\n            color: #ffffff !important;\n            line-height: 1.1 !important;\n        }',
        '            font-size: 20px !important;\n            font-weight: 700 !important;\n            color: #ffffff !important;\n            line-height: 1.2 !important;\n            white-space: nowrap !important;\n        }'
    ),
    (
        '#botRunningSaldo {\n            font-size: 26px !important;',
        '#botRunningSaldo {\n            font-size: 20px !important;'
    ),
    (
        "const cor = lucroLiquido > 0 ? '#4caf50' : lucroLiquido < 0 ? '#f44336' : '#888';",
        "const cor = lucroLiquido > 0.005 ? '#4caf50' : lucroLiquido < -0.005 ? '#f44336' : '#4caf50';"
    ),
]
for old, new in fixes:
    if old in html:
        html = html.replace(old, new, 1); count += 1; print(f"FIX {count} aplicado")
    else:
        print(f"nao encontrado: {old[:40]}")
open(HTML, "w", encoding="utf-8").write(html)
print(f"Pronto! {count} fixes.")
