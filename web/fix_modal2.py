import shutil
HTML = "/home/dirlei/alpha-dolar-2.0/web/dashboard-fixed.html"
shutil.copy2(HTML, HTML + ".backup2")
print("Backup criado")
html = open(HTML, encoding="utf-8").read()
count = 0
OLD1 = ("            position: fixed;\n"
        "            top: 0; left: 0; right: 0; bottom: 0;\n"
        "            width: 100%;\n"
        "            height: 100%;\n"
        "            background: rgba(0,0,0,0.78);\n"
        "            backdrop-filter: blur(2px);\n"
        "            display: none;\n"
        "            align-items: center;\n"
        "            justify-content: center;\n"
        "            z-index: 99999;\n"
        "            pointer-events: auto;\n"
        "            padding: 20px;\n"
        "            box-sizing: border-box;")
NEW1 = ("            position: fixed;\n"
        "            top: 56px;\n"
        "            left: 0;\n"
        "            width: 340px;\n"
        "            height: calc(100vh - 56px);\n"
        "            background: transparent;\n"
        "            backdrop-filter: none;\n"
        "            display: none;\n"
        "            align-items: flex-start;\n"
        "            justify-content: flex-start;\n"
        "            z-index: 99999;\n"
        "            pointer-events: none;\n"
        "            padding: 0;\n"
        "            box-sizing: border-box;")
if OLD1 in html:
    html = html.replace(OLD1, NEW1, 1); count += 1; print("FIX 1 aplicado")
else:
    print("FIX 1 nao encontrado")
OLD2 = ("            pointer-events: auto;\n"
        "            background: #1e2128;\n"
        "            border-radius: 16px;\n"
        "            width: 100%;\n"
        "            max-width: 420px;\n"
        "            max-height: calc(100vh - 60px);\n"
        "            overflow-y: auto;\n"
        "            overflow-x: hidden;\n"
        "            box-shadow: 0 20px 60px rgba(0,0,0,0.6);\n"
        "            border: 1px solid #2a2d35;\n"
        "            padding: 0;\n"
        "            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;\n"
        "            scrollbar-width: thin;\n"
        "            scrollbar-color: #333 transparent;")
NEW2 = ("            pointer-events: auto;\n"
        "            background: #13151a;\n"
        "            border-radius: 0;\n"
        "            width: 340px;\n"
        "            height: 100%;\n"
        "            overflow-y: auto;\n"
        "            overflow-x: hidden;\n"
        "            box-shadow: 2px 0 12px rgba(0,0,0,0.3);\n"
        "            border-right: 1px solid #2a2d35;\n"
        "            padding: 0;\n"
        "            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;\n"
        "            scrollbar-width: thin;\n"
        "            scrollbar-color: #333 transparent;")
if OLD2 in html:
    html = html.replace(OLD2, NEW2, 1); count += 1; print("FIX 2 aplicado")
else:
    print("FIX 2 nao encontrado")
OLD3 = ("                // Lucro — só calcula se tiver saldoInicial válido\n"
        "                const lucroLiquido  = (saldoInicial > 0 && saldoAtual > 0) ? (saldoAtual - saldoInicial) : 0;\n"
        "                const profitPercent = saldoInicial > 0 ? ((lucroLiquido / saldoInicial) * 100) : 0;\n"
        "                lucroAcumulado = lucroLiquido;")
NEW3 = ("                // Lucro — só atualiza se saldo realmente mudou do inicial\n"
        "                const lucroLiquido  = (saldoInicial > 0 && saldoAtual > 0 && Math.abs(saldoAtual - saldoInicial) > 0.001)\n"
        "                    ? (saldoAtual - saldoInicial) : lucroAcumulado;\n"
        "                const profitPercent = saldoInicial > 0 ? ((lucroLiquido / saldoInicial) * 100) : 0;\n"
        "                lucroAcumulado = lucroLiquido;")
if OLD3 in html:
    html = html.replace(OLD3, NEW3, 1); count += 1; print("FIX 3 aplicado")
else:
    print("FIX 3 nao encontrado")
open(HTML, "w", encoding="utf-8").write(html)
print(f"Pronto! {count} fixes aplicados.")
