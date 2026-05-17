"""
Testa se a quota da API do Google está liberada e lista contas/locais.
Uso: python test_quota.py
"""
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

import httpx
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

_env = Path(__file__).parent / ".env"
for line in _env.read_text(encoding="utf-8").splitlines():
    if "=" in line and not line.startswith("#"):
        import os
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())

import os

CLIENT_ID     = os.environ["GOOGLE_CLIENT_ID"]
CLIENT_SECRET = os.environ["GOOGLE_CLIENT_SECRET"]
REFRESH_TOKEN = os.environ["GOOGLE_REFRESH_TOKEN"]

SCOPES = ["https://www.googleapis.com/auth/business.manage"]

print("Agenty — Teste de quota Google Business Profile API")
print("=" * 55)

# 1. Renovar token de acesso
print("\n[1/3] Renovando access token...")
creds = Credentials(
    token=None,
    refresh_token=REFRESH_TOKEN,
    token_uri="https://oauth2.googleapis.com/token",
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    scopes=SCOPES,
)
try:
    creds.refresh(Request())
    print(f"  OK — token renovado, expira em: {creds.expiry}")
except Exception as e:
    print(f"  ERRO ao renovar token: {e}")
    print("  Execute oauth_setup.py novamente para re-autorizar.")
    sys.exit(1)

headers = {"Authorization": f"Bearer {creds.token}"}

# 2. Listar contas
print("\n[2/3] Listando contas do Google Business Profile...")
resp = httpx.get(
    "https://mybusinessaccountmanagement.googleapis.com/v1/accounts",
    headers=headers, timeout=15,
)
print(f"  Status HTTP: {resp.status_code}")

if resp.status_code == 403:
    data = resp.json()
    print(f"  QUOTA BLOQUEADA: {data.get('error', {}).get('message', resp.text[:300])}")
    print("\n  Acesse: console.cloud.google.com → APIs → My Business Account Management API")
    print("  Clique em 'request' para solicitar cota de producao.")
    sys.exit(1)

if resp.status_code != 200:
    print(f"  Erro inesperado: {resp.text[:400]}")
    sys.exit(1)

accounts = resp.json().get("accounts", [])
if not accounts:
    print("  Nenhuma conta encontrada. O perfil no Google Meu Negocio precisa estar verificado.")
    sys.exit(1)

print(f"  {len(accounts)} conta(s) encontrada(s):")
for i, acc in enumerate(accounts):
    print(f"    [{i}] {acc.get('accountName')} — {acc.get('name')}")

account = accounts[0]
account_name = account["name"]

# 3. Listar locais
print(f"\n[3/3] Listando locais da conta '{account.get('accountName')}'...")
resp2 = httpx.get(
    f"https://mybusinessbusinessinformation.googleapis.com/v1/{account_name}/locations",
    headers=headers,
    params={"readMask": "name,title"},
    timeout=15,
)
print(f"  Status HTTP: {resp2.status_code}")

if resp2.status_code == 403:
    data = resp2.json()
    print(f"  QUOTA BLOQUEADA (Business Information API): {data.get('error', {}).get('message', resp2.text[:300])}")
    print("\n  Ative a API: console.cloud.google.com → Biblioteca → 'My Business Business Information API'")
    sys.exit(1)

if resp2.status_code != 200:
    print(f"  Erro inesperado: {resp2.text[:400]}")
    sys.exit(1)

locations = resp2.json().get("locations", [])
if not locations:
    print("  Nenhum local encontrado nesta conta.")
    sys.exit(1)

print(f"  {len(locations)} local(is) encontrado(s):")
for i, loc in enumerate(locations):
    raw   = loc.get("name", "")       # locations/Y
    v4    = f"{account_name}/{raw}"   # accounts/X/locations/Y
    print(f"    [{i}] {loc.get('title')}")
    print(f"         GOOGLE_ACCOUNT_NAME={account_name}")
    print(f"         GOOGLE_LOCATION_NAME={v4}")

# 4. Testar reviews API
print(f"\n[BONUS] Testando My Business Reviews API...")
loc_v4 = f"{account_name}/{locations[0]['name']}"
resp3 = httpx.get(
    f"https://mybusiness.googleapis.com/v4/{loc_v4}/reviews",
    headers=headers,
    params={"pageSize": 5},
    timeout=15,
)
print(f"  Status HTTP: {resp3.status_code}")
if resp3.status_code == 200:
    reviews = resp3.json().get("reviews", [])
    total   = resp3.json().get("totalReviewCount", "?")
    print(f"  Reviews API: OK — {total} avaliacoes totais, {len(reviews)} retornadas")
elif resp3.status_code == 403:
    data = resp3.json()
    print(f"  QUOTA BLOQUEADA (Reviews API): {data.get('error', {}).get('message', resp3.text[:300])}")
    print("  Ative: console.cloud.google.com → Biblioteca → 'My Business Reviews API'")
else:
    print(f"  Resposta: {resp3.text[:400]}")

print("\n" + "=" * 55)
print("Cole os valores GOOGLE_ACCOUNT_NAME e GOOGLE_LOCATION_NAME no .env")
print("e mude MOCK_MODE=false para usar a API real.")
