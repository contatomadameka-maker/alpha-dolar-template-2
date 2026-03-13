"""
Alpha Dolar — Sistema de Sinais Telegram
Envia sinais automáticos e manuais para o canal
"""
import asyncio
import json
import threading
import time
import requests
from datetime import datetime
import pytz

TELEGRAM_TOKEN = "8223914227:AAHzCTOZxqxzGY7yEfvr_lqeFvEhXm0228Y"
CHANNEL_ID = "-1003524534332"
BR_TZ = pytz.timezone("America/Sao_Paulo")

def agora_br():
    return datetime.now(BR_TZ).strftime("%H:%M:%S")

def enviar_telegram(texto):
    try:
        r = requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            json={"chat_id": CHANNEL_ID, "text": texto, "parse_mode": "HTML"},
            timeout=10
        )
        return r.json().get("ok", False)
    except Exception as e:
        print(f"Erro Telegram: {e}")
        return False

def sinal_digitos(mercado, tipo, probabilidade, digitos_recentes):
    emoji = "🟢" if tipo in ["DIGITEVEN", "DIGITOVER"] else "🔴"
    tipo_legivel = {
        "DIGITEVEN": "PAR",
        "DIGITODD": "ÍMPAR", 
        "DIGITOVER": "ACIMA DE 4",
        "DIGITUNDER": "ABAIXO DE 5"
    }.get(tipo, tipo)
    
    msg = f"""🔮 <b>ALPHA PATTERN — SINAL DETECTADO</b>

{emoji} <b>Tipo:</b> {tipo_legivel}
📊 <b>Mercado:</b> {mercado}
🎯 <b>Probabilidade:</b> {probabilidade}%
🔢 <b>Últimos dígitos:</b> {' '.join(str(d) for d in digitos_recentes[-8:])}
🕐 <b>Horário:</b> {agora_br()} (Brasília)

⚠️ <i>Use gestão de banca. Risco é sua responsabilidade.</i>
🌐 alphadolar.online"""
    return enviar_telegram(msg)

def sinal_rise_fall(mercado, direcao, confianca, preco_entrada):
    emoji = "📈" if direcao == "CALL" else "📉"
    direcao_legivel = "SUBIDA (CALL)" if direcao == "CALL" else "QUEDA (PUT)"
    
    msg = f"""⚡ <b>ALPHA IA PRO — SINAL RISE/FALL</b>

{emoji} <b>Direção:</b> {direcao_legivel}
📊 <b>Mercado:</b> {mercado}
💹 <b>Entrada:</b> {preco_entrada}
🎯 <b>Confiança IA:</b> {confianca}%
🕐 <b>Horário:</b> {agora_br()} (Brasília)

⚠️ <i>Sinal gerado por IA. Opere com responsabilidade.</i>
🌐 alphadolar.online"""
    return enviar_telegram(msg)

def sinal_horario(faixa, score, recomendacao):
    if score >= 80:
        emoji = "🔥"
        status = "ÓTIMO PARA OPERAR"
    elif score >= 65:
        emoji = "✅"
        status = "BOM PARA OPERAR"
    else:
        emoji = "⚠️"
        status = "OPERAR COM CAUTELA"
    
    msg = f"""⏰ <b>ALPHA CLOCK — ALERTA DE HORÁRIO</b>

{emoji} <b>Status:</b> {status}
🕐 <b>Faixa:</b> {faixa}
📊 <b>Score:</b> {score}%
💡 <b>Recomendação:</b> {recomendacao}
🕐 <b>Agora:</b> {agora_br()} (Brasília)

🌐 alphadolar.online"""
    return enviar_telegram(msg)

def sinal_volatilidade(mercado, nivel, ratio):
    if nivel == "PERIGO":
        emoji = "🚨"
        acao = "PARE as operações agora!"
    elif nivel == "ATENÇÃO":
        emoji = "⚠️"
        acao = "Reduza o stake em 50%"
    else:
        emoji = "🛡️"
        acao = "Condições normais para operar"
    
    msg = f"""🛡️ <b>ALPHA SHIELD — ALERTA DE VOLATILIDADE</b>

{emoji} <b>Nível:</b> {nivel}
📊 <b>Mercado:</b> {mercado}
📈 <b>Ratio volatilidade:</b> {ratio:.2f}x
💡 <b>Ação:</b> {acao}
🕐 <b>Horário:</b> {agora_br()} (Brasília)

🌐 alphadolar.online"""
    return enviar_telegram(msg)

def sinal_resultado(tipo, mercado, resultado, lucro, win_rate):
    emoji = "✅" if resultado == "won" else "❌"
    cor = "💚" if resultado == "won" else "🔴"
    
    msg = f"""{emoji} <b>RESULTADO — ALPHA DOLAR</b>

{cor} <b>Resultado:</b> {"WIN" if resultado == "won" else "LOSS"}
📊 <b>Mercado:</b> {mercado}
💰 <b>Lucro:</b> {"+" if lucro >= 0 else ""}${lucro:.2f}
🎯 <b>Win Rate sessão:</b> {win_rate}%
🕐 <b>Horário:</b> {agora_br()} (Brasília)

🌐 alphadolar.online"""
    return enviar_telegram(msg)

def sinal_manual(texto_livre):
    msg = f"""📢 <b>ALPHA SIGNALS — AVISO</b>

{texto_livre}

🕐 {agora_br()} (Brasília)
🌐 alphadolar.online"""
    return enviar_telegram(msg)

# Exportar funções
__all__ = [
    'enviar_telegram', 'sinal_digitos', 'sinal_rise_fall',
    'sinal_horario', 'sinal_volatilidade', 'sinal_resultado', 'sinal_manual'
]
