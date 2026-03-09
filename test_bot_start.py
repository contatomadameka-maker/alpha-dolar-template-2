import sys
sys.path.insert(0, '/home/dirlei/alpha-dolar-2.0')
sys.path.insert(0, '/home/dirlei/alpha-dolar-2.0/backend')

print("🧪 Testando início do bot como a API faz...")

from backend.bot import AlphaDolar
from backend.strategies.alpha_bot_1 import AlphaBot1
import threading
import time

strategy = AlphaBot1()
bot = AlphaDolar(strategy=strategy, use_martingale=False)

print("✅ Bot criado")

def run_bot():
    print("🚀 Thread do bot iniciada")
    try:
        result = bot.start()
        print(f"✅ bot.start() retornou: {result}")
    except Exception as e:
        print(f"❌ Erro no bot.start(): {e}")
        import traceback
        traceback.print_exc()

print("🎬 Iniciando thread...")
thread = threading.Thread(target=run_bot, daemon=True)
thread.start()

print("⏳ Aguardando 30 segundos...")
time.sleep(30)

print("🛑 Parando bot...")
bot.stop()

print("✅ Teste concluído")
