import os
import requests

SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY', '')

HEADERS = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
}

def init_db():
    print("Supabase conectado!")

def salvar_cliente(data):
    deriv_id = data.get('deriv_id')
    url = f"{SUPABASE_URL}/rest/v1/clientes"
    payload = {
        'deriv_id': deriv_id,
        'nome': data.get('nome'),
        'email': data.get('email'),
        'token_demo': data.get('token_demo'),
        'token_real': data.get('token_real'),
        'account_type': data.get('account_type', 'demo'),
        'bot_name': data.get('bot_name', ''),
    }
    # Tenta insert primeiro
    r = requests.post(url, json=payload, headers={**HEADERS, 'Prefer': 'return=representation'})
    if r.status_code in [200, 201]:
        return True
    # Se já existe, faz update
    r = requests.patch(f"{url}?deriv_id=eq.{deriv_id}", json=payload, headers=HEADERS)
    return r.status_code in [200, 204]

def listar_clientes():
    url = f"{SUPABASE_URL}/rest/v1/clientes?order=ultimo_acesso.desc"
    r = requests.get(url, headers=HEADERS)
    if r.status_code == 200:
        return r.json()
    return []

def salvar_operacao(bot_name, cliente_id, direcao, ganhou, lucro, stake):
    import requests as req
    import os
    SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
    SUPABASE_KEY = os.environ.get('SUPABASE_KEY', '')
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json'
    }
    payload = {
        'bot_name': bot_name,
        'cliente_id': cliente_id,
        'tipo': direcao,
        'stake': float(stake),
        'resultado': 'win' if ganhou else 'loss',
        'lucro': float(lucro)
    }
    try:
        req.post(f"{SUPABASE_URL}/rest/v1/operacoes", json=payload, headers=headers)
    except:
        pass

def listar_operacoes(bot_name=None):
    import requests as req
    import os
    SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
    SUPABASE_KEY = os.environ.get('SUPABASE_KEY', '')
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json'
    }
    url = f"{SUPABASE_URL}/rest/v1/operacoes?order=criado_em.desc&limit=500"
    if bot_name:
        url += f"&bot_name=eq.{bot_name}"
    try:
        r = req.get(url, headers=headers)
        if r.status_code == 200:
            return r.json()
    except: pass
    return []

def listar_bots():
    import requests as req, os
    SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
    SUPABASE_KEY = os.environ.get('SUPABASE_KEY', '')
    headers = {'apikey': SUPABASE_KEY, 'Authorization': f'Bearer {SUPABASE_KEY}'}
    r = req.get(f"{SUPABASE_URL}/rest/v1/bots?order=criado_em.desc", headers=headers)
    return r.json() if r.status_code == 200 else []

def salvar_bot(data):
    import requests as req, os
    SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
    SUPABASE_KEY = os.environ.get('SUPABASE_KEY', '')
    headers = {
        'apikey': SUPABASE_KEY, 'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json',
        'Prefer': 'resolution=merge-duplicates,return=representation'
    }
    payload = {'nome': data.get('nome'), 'dono': data.get('dono'), 'deriv_id': data.get('deriv_id'), 'status': data.get('status','ativo')}
    r = req.post(f"{SUPABASE_URL}/rest/v1/bots", json=payload, headers=headers)
    return r.status_code in [200, 201]

def atualizar_bot(nome, data):
    import requests as req, os
    SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
    SUPABASE_KEY = os.environ.get('SUPABASE_KEY', '')
    headers = {'apikey': SUPABASE_KEY, 'Authorization': f'Bearer {SUPABASE_KEY}', 'Content-Type': 'application/json'}
    r = req.patch(f"{SUPABASE_URL}/rest/v1/bots?nome=eq.{nome}", json=data, headers=headers)
    return r.status_code in [200, 204]
