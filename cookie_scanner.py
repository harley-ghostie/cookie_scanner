import requests
import re
import argparse
import os
import subprocess
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

def analisar_cookies_http(url):
    try:
        response = requests.get(url, verify=False, timeout=10)
        cookies = response.headers.get('Set-Cookie')

        print(f"\n[+] Analisando cookies HTTP em: {url}")
        if not cookies:
            print("  [!] Nenhum cookie identificado.\n")
            return

        for raw_cookie in cookies.split(','):
            raw_cookie = raw_cookie.strip()
            print(f"\n  Cookie bruto: {raw_cookie}")
            lower = raw_cookie.lower()

            if 'secure' not in lower:
                print("    ⚠ Falta o atributo Secure")
            if 'httponly' not in lower:
                print("    ⚠ Falta o atributo HttpOnly")
            if 'samesite' not in lower:
                print("    ⚠ Falta o atributo SameSite")
            elif 'samesite=none' in lower and 'secure' not in lower:
                print("    ⚠ SameSite=None exige Secure")

            if 'expires=' in lower or 'max-age=' in lower:
                print("    ⚠ Cookie persistente detectado")

            if any(s in lower for s in ['sessionid', 'token', 'auth']):
                print("    ⚠ Possível dado sensível em cookie")

    except Exception as e:
        print(f"  [ERRO] Erro ao acessar {url}: {e}")

def buscar_e_analisar_scripts(url, html):
    soup = BeautifulSoup(html, 'html.parser')
    scripts = [script.get('src') for script in soup.find_all('script') if script.get('src')]

    for src in scripts:
        src_url = urljoin(url, src)
        try:
            r = requests.get(src_url, verify=False, timeout=10)
            print(f"\n[+] Analisando JS externo: {src_url}")
            analisar_dom_cookie_codigo(r.text)
        except Exception as e:
            print(f"  [ERRO] Falha ao baixar {src_url}: {e}")

def analisar_dom_cookie_manipulation(url):
    try:
        response = requests.get(url, verify=False, timeout=10)
        html = response.text

        print(f"\n[+] Analisando DOM principal para manipulação de cookies em: {url}")
        analisar_dom_cookie_codigo(html)
        buscar_e_analisar_scripts(url, html)

    except Exception as e:
        print(f"  [ERRO] Falha ao carregar página: {e}")

def analisar_dom_cookie_codigo(source_code):
    usos_cookie = re.findall(r'document\.cookie\s*=\s*.*?;', source_code, re.IGNORECASE)

    if not usos_cookie:
        print("  [✓] Nenhuma manipulação de cookie via DOM detectada.")
        return

    for uso in usos_cookie:
        print(f"\n  Uso de document.cookie: {uso.strip()}")
        if any(fonte in uso.lower() for fonte in ['location', 'referrer', 'window.name', 'localstorage']):
            print("    ⚠ Possível manipulação baseada em entrada do usuário!")
        else:
            print("    ⚠ Uso encontrado – verificar se o valor usado é estático ou oriundo do backend.\n")

def executar_dirsearch(url):
    print(f"\n[+] Executando dirsearch em {url}")
    comando = [
        "dirsearch",
        "-u", url,
        "-e", "php,aspx,js,html,json",
        "--plain-text-report=dirsearch_result.txt"
    ]
    subprocess.run(comando)

    if os.path.exists("dirsearch_result.txt"):
        with open("dirsearch_result.txt") as f:
            paths = [line.strip() for line in f.readlines() if url in line]
        return paths
    return []

def executar_teste_completo(url):
    analisar_cookies_http(url)
    analisar_dom_cookie_manipulation(url)

    discovered_paths = executar_dirsearch(url)
    for path in discovered_paths:
        print(f"\n[+] Analisando endpoint descoberto: {path}")
        analisar_cookies_http(path)
        analisar_dom_cookie_manipulation(path)

if __name__ == "__main__":
    import warnings
    warnings.filterwarnings("ignore")

    parser = argparse.ArgumentParser(description="Scanner de cookies inseguros + DOM Cookie Manipulation + Dirsearch")
    parser.add_argument("-u", "--url", required=True, help="URL alvo (ex: https://site.com)")
    parser.add_argument("--full", action="store_true", help="Executar análise completa com dirsearch")

    args = parser.parse_args()
    alvo = args.url.strip("/")

    if args.full:
        executar_teste_completo(alvo)
    else:
        analisar_cookies_http(alvo)
        analisar_dom_cookie_manipulation(alvo)
