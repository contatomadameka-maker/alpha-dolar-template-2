with open('trading-button-fix.js', 'r') as f:
    lines = f.readlines()

with open('trading-button-fix.js', 'w') as f:
    for line in lines:
        if 'await fetch`${API_URL}/bot/stop`' in line:
            line = line.replace('fetch`${API_URL}/bot/stop`', 'fetch(`${API_URL}/bot/stop`')
        if 'await fetch`${API_URL}/bot/start`' in line:
            line = line.replace('fetch`${API_URL}/bot/start`', 'fetch(`${API_URL}/bot/start`')
        f.write(line)

print("Corrigido!")
