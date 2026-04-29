# Cookie Security Scanner & Session Validation
![Status](https://img.shields.io/badge/STATUS-EM%20DESENVOLVIMENTO-brightgreen?style=for-the-badge)
> [!NOTE]
> Projeto em desenvolvimento.
>
> Este repositório reúne scripts de apoio para validação técnica e triagem de segurança. Os scripts podem passar por ajustes, refatoração e melhorias de precisão conforme novos cenários forem testados.

Repositório com scripts para validação de segurança em cookies HTTP, manipulação de cookies no DOM e teste controlado de validade de sessão autenticada.

A proposta deste repositório é apoiar análises autorizadas de segurança em aplicações web, principalmente em cenários de pentest, validação de configuração de cookies e investigação de exposição relacionada a sessão.

---

## Scripts disponíveis

| Script | Objetivo | Quando usar |
|---|---|---|
| `cookie_scanner.py` | Analisa cookies HTTP, atributos de segurança, uso de `document.cookie` no DOM e, opcionalmente, endpoints descobertos via `dirsearch`. | Usar na fase de análise inicial da aplicação para identificar cookies sem `Secure`, `HttpOnly`, `SameSite`, cookies persistentes e manipulação insegura via JavaScript. |
| `script_cookie.py` | Valida se um cookie de sessão informado ainda permite acesso a uma área autenticada da aplicação. | Usar apenas em ambiente autorizado para confirmar se uma sessão capturada, fornecida pelo cliente ou obtida em teste controlado ainda está ativa. |

---

## Visão geral

Este repositório possui dois scripts com finalidades diferentes, mas complementares.

O `cookie_scanner.py` é voltado para **análise de configuração e exposição de cookies**. Ele verifica headers HTTP, atributos de segurança e possíveis manipulações de cookies no código JavaScript da página.

O `script_cookie.py` é voltado para **validação pontual de sessão**. Ele envia uma requisição autenticada usando um cookie definido manualmente e verifica se uma palavra-chave esperada aparece na resposta.

---

## 1. cookie_scanner.py

### Descrição

O `cookie_scanner.py` é um scanner simples para identificar problemas comuns relacionados a cookies em aplicações web.

Ele analisa os cookies retornados pelo servidor e verifica se estão presentes atributos importantes de segurança, como:

```text
Secure
HttpOnly
SameSite
```

Além disso, o script também procura usos de `document.cookie` no HTML principal e em arquivos JavaScript externos, ajudando a identificar possíveis manipulações de cookie no lado do cliente.

Opcionalmente, o script pode executar o `dirsearch` para descobrir novos paths e aplicar a mesma análise nos endpoints encontrados.

---

### O que o script faz

O script executa as seguintes verificações:

- identifica cookies retornados no header `Set-Cookie`;
- verifica ausência do atributo `Secure`;
- verifica ausência do atributo `HttpOnly`;
- verifica ausência do atributo `SameSite`;
- identifica uso de `SameSite=None` sem `Secure`;
- identifica cookies persistentes com `Expires` ou `Max-Age`;
- alerta sobre cookies com nomes possivelmente sensíveis, como `sessionid`, `token` ou `auth`;
- analisa o HTML da página em busca de `document.cookie`;
- baixa scripts JavaScript externos e procura manipulação de cookies;
- opcionalmente executa `dirsearch` para descobrir novos endpoints e analisá-los.

---

### Cenários indicados:

```text
Validação de cookies de sessão
Análise de headers Set-Cookie
Verificação de Secure, HttpOnly e SameSite
Busca por manipulação de cookies via JavaScript
Triagem de aplicações legadas
Validação de achados automatizados
Análise de endpoints descobertos
```

---

### Exemplo básico

```bash
python3 cookie_scanner.py -u "https://exemplo.com.br"
```

---

### Exemplo com análise completa usando dirsearch

```bash
python3 cookie_scanner.py -u "https://exemplo.com.br" --full
```

---

### Campos ajustáveis no script

O principal campo informado por linha de comando é:

```bash
-u "https://exemplo.com.br"
```

Esse valor representa a URL base da aplicação que será analisada.

No modo completo, o script executa o `dirsearch` com as seguintes extensões:

```python
"-e", "php,aspx,js,html,json"
```

Caso necessário, essa lista pode ser ajustada para incluir outras extensões, como:

```text
jsp
do
action
api
txt
xml
bak
old
```

---

### Dependências

O script utiliza as seguintes dependências Python:

```text
requests
beautifulsoup4
```

Instalação:

```bash
python3 -m pip install requests beautifulsoup4
```

O `dirsearch` é utilizado apenas quando o modo `--full` é executado no `cookie_scanner.py`.

Ele pode ser instalado pelo repositório do Kali:

```bash
sudo apt update
sudo apt install dirsearch
```

Depois, valide se o comando está acessível:

```bash
dirsearch -h
```

Caso o pacote do Kali não esteja disponível ou esteja desatualizado, instale a versão oficial pelo repositório do projeto:
```bash
git clone https://github.com/maurosoria/dirsearch.git
cd dirsearch
python3 -m pip install -r requirements.txt
```
Nesse caso, ajuste o comando dentro da função `executar_dirsearch()`ou adicione o diretório do projeto ao PATH.
Se você usa zsh em ves de bash, troque `~/.bashrc` por `~/.zshrc`:
```bash
echo 'export PATH="$PATH:/opt/dirsearch"' >> ~/.bashrc
source ~/.bashrc
```
Depois, valide se o comando está acessível:

```bash
dirsearch -h
```
---

### Saída esperada

Exemplo de alerta para cookie sem atributos de segurança:

```text
[+] Analisando cookies HTTP em: https://exemplo.com.br

Cookie bruto: PHPSESSID=abc123; path=/
    ⚠ Falta o atributo Secure
    ⚠ Falta o atributo HttpOnly
    ⚠ Falta o atributo SameSite
    ⚠ Possível dado sensível em cookie
```

Exemplo de alerta para manipulação via DOM:

```text
Uso de document.cookie: document.cookie = "token=" + location.hash;
    ⚠ Possível manipulação baseada em entrada do usuário!
```

---

### Interpretação dos resultados

A ausência de `Secure`, `HttpOnly` ou `SameSite` não significa, isoladamente, exploração confirmada. Esses achados indicam fragilidade de configuração e devem ser analisados conforme o tipo de cookie, sensibilidade da aplicação e contexto de uso.

Para cookies de sessão autenticada, a ausência de `HttpOnly` e `Secure` tende a ser mais relevante, pois pode aumentar o impacto de ataques como XSS, interceptação em tráfego inseguro ou roubo de sessão.

---

## 2. script_cookie.py

### Descrição

O `script_cookie.py` é um script simples para validar se um cookie de sessão informado manualmente ainda permite acesso a uma área autenticada da aplicação.

Ele envia uma requisição HTTP para uma URL protegida usando o cookie configurado no script. Em seguida, verifica se uma palavra-chave esperada aparece no HTML da resposta.

Se a palavra-chave for encontrada, o script indica que a sessão aparenta estar ativa.

---

### O que o script faz

O script executa as seguintes ações:

- define manualmente um cookie de sessão;
- envia requisição HTTP para uma URL protegida;
- inclui o cookie no header `Cookie`;
- procura uma palavra-chave esperada na resposta;
- informa se a sessão parece ativa ou inválida.

---

### Quando usar

Use este script apenas em cenários autorizados, como:

```text
Validação de sessão fornecida pelo cliente
Teste controlado de expiração de sessão
Confirmação de impacto após roubo de cookie em laboratório
Validação de sessão após logout
Teste de persistência indevida de autenticação
Verificação de timeout de sessão
```

Este script não deve ser usado com cookies de terceiros, sessões reais sem autorização ou ambientes fora do escopo.

---

### Campos que devem ser alterados

Antes de executar, altere os seguintes campos:

```python
PHPSESSID = "VALOR_DO_COOKIE_AQUI"
```

Informe o cookie de sessão que será validado.

Exemplo genérico:

```python
PHPSESSID = "abc123def456"
```

Também altere a URL protegida:

```python
target_url = "https://exemplo.com.br/area-logada"
```

Esse endpoint deve ser uma página que só retorna conteúdo específico quando o usuário está autenticado.

Altere também a palavra-chave de sucesso:

```python
auth_keyword = "Bem-vindo"
```

Esse valor deve ser um texto que aparece apenas quando o acesso autenticado é válido.

Exemplos:

```text
Bem-vindo
Minha conta
Dashboard
Sair
Área restrita
Perfil
```

---

### Exemplo de execução

```bash
python3 script_cookie.py
```

---

### Saída esperada

Sessão ativa:

```text
[+] Sessão ativa: acesso autorizado.
```

Sessão inválida ou expirada:

```text
[-] Sessão inválida ou expirada.
```

---

### Observação importante sobre cookies

O script atual utiliza o header `Cookie` manualmente.

Caso o cookie tenha nome diferente de `PHPSESSID`, ajuste o header:

```python
headers = {
    "User-Agent": "Mozilla/5.0",
    "Cookie": "NOME_DO_COOKIE=VALOR_DO_COOKIE"
}
```

Exemplo:

```python
headers = {
    "User-Agent": "Mozilla/5.0",
    "Cookie": "JSESSIONID=abc123def456"
}
```

Para múltiplos cookies:

```python
headers = {
    "User-Agent": "Mozilla/5.0",
    "Cookie": "PHPSESSID=abc123; token=xyz456; theme=dark"
}
```

---

## Fluxo recomendado de uso

A ordem recomendada é:

```text
1. Executar cookie_scanner.py na aplicação
   ↓
2. Identificar cookies sensíveis ou mal configurados
   ↓
3. Validar se há manipulação de document.cookie
   ↓
4. Caso exista cookie de sessão autorizado para teste, usar script_cookie.py
   ↓
5. Confirmar se a sessão permanece ativa em endpoint protegido
```

---

## Recomendações de mitigação

Cookies de sessão devem utilizar os atributos `Secure`, `HttpOnly` e `SameSite` de acordo com o contexto da aplicação. O atributo `Secure` garante envio apenas por HTTPS, `HttpOnly` reduz o risco de acesso ao cookie por JavaScript em caso de XSS, e `SameSite` ajuda a reduzir exposição a ataques de CSRF.

Também é recomendado revisar cookies persistentes, reduzir tempo de vida de sessões, invalidar sessão após logout, rotacionar identificadores após autenticação, evitar armazenamento de dados sensíveis diretamente em cookies e impedir manipulação insegura via `document.cookie`.

Quando houver manipulação de cookies no lado do cliente, valide se os valores não são derivados de fontes controláveis pelo usuário, como `location`, `referrer`, `window.name` ou `localStorage`, sem sanitização adequada.

---


## Limitações

O `cookie_scanner.py` realiza uma análise simples baseada em headers, HTML e JavaScript baixado diretamente da página. Ele pode não identificar cookies criados dinamicamente após interações complexas, autenticação, navegação em SPA ou execução avançada de JavaScript.

O `script_cookie.py` depende de uma palavra-chave para inferir sessão ativa. Se a aplicação mudar o texto, idioma ou estrutura da página, o resultado pode ser falso negativo ou falso positivo.

Para validação mais completa, combine estes scripts com análise manual, navegador, proxy interceptador e revisão das configurações do backend.

---

## Aviso legal

Estes scripts devem ser utilizados apenas em ambientes autorizados.

A finalidade é apoiar validações técnicas, pentests autorizados, análise defensiva, hardening de cookies e verificação controlada de sessões.

O uso contra sistemas sem autorização é proibido.
