import httpx

try:
    response = httpx.get("https://www.google.com")
    print("Conexão bem-sucedida, status code:", response.status_code)
except Exception as e:
    print("Erro na conexão:", e)
