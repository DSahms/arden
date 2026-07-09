import urllib.request, urllib.error, socket

for name, url in [('LM Studio', 'http://localhost:1234'), ('Ollama', 'http://localhost:11434')]:
    try:
        urllib.request.urlopen(url, timeout=3)
        print(f'{name}: RUNNING')
    except Exception as e:
        print(f'{name}: NOT RUNNING ({type(e).__name__})')

try:
    s = socket.create_connection(('localhost', 7687), timeout=3)
    s.close()
    print('Neo4j: RUNNING')
except Exception as e:
    print(f'Neo4j: NOT RUNNING ({type(e).__name__})')
