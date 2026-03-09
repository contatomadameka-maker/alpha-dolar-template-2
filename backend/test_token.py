# Teste rápido de token
import sys

def is_demo_token(token):
    """Verifica se é token de conta DEMO"""
    # Tokens DEMO da Deriv começam com VRTC (Virtual Trading Center)
    return token.startswith('VRTC') if token else False

# Seu token
token = sys.argv[1] if len(sys.argv) > 1 else ""

if is_demo_token(token):
    print(f"✅ TOKEN DEMO detectado: {token[:10]}...")
    print("   📊 Conta: Virtual (Demo)")
    print("   💰 Dinheiro: Virtual")
else:
    print(f"⚠️ TOKEN REAL detectado: {token[:10]}...")
    print("   📊 Conta: Real")
    print("   💰 Dinheiro: REAL - CUIDADO!")

