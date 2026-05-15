"""
Agenty — Setup OAuth2 Google Business Profile
Execute uma vez por cliente para autorizar o acesso e salvar as credenciais no .env.

Uso:
    python oauth_setup.py
"""
import json
import sys
from pathlib import Path

import httpx
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES   = ["https://www.googleapis.com/auth/business.manage"]
ENV_FILE = Path(__file__).parent / ".env"
SECRETS  = Path(__file__).parent / "client_secrets.json"


def _save(key: str, value: str):
    lines = ENV_FILE.read_text(encoding="utf-8").splitlines() if ENV_FILE.exists() else []
    index = {l.split("=", 1)[0].strip(): i for i, l in enumerate(lines)
             if "=" in l and not l.startswith("#")}
    entry = f"{key}={value}"
    if key in index:
        lines[index[key]] = entry
    else:
        lines.append(entry)
    ENV_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"    {key} salvo")


def main():
    print("\nAgenty — Setup OAuth2 Google Business Profile")
    print("=" * 50)

    if not SECRETS.exists():
        print("\nERRO: client_secrets.json nao encontrado.")
        print("Para obte-lo:")
        print("  1. Acesse console.cloud.google.com")
        print("  2. Crie um projeto e ative a API Google My Business")
        print("  3. Credenciais > Criar credencial > OAuth 2.0 > App da Web")
        print("  4. Baixe o JSON e renomeie para client_secrets.json nesta pasta")
        sys.exit(1)

    # --- Passo 1: OAuth ---
    print("\n[1/3] Abrindo browser para autorizacao...")
    print("      Faca login com a conta Google do negocio e clique em Permitir.\n")
    flow  = InstalledAppFlow.from_client_secrets_file(str(SECRETS), SCOPES)
    creds = flow.run_local_server(port=8080, prompt="consent", open_browser=True)

    _save("GOOGLE_REFRESH_TOKEN", creds.refresh_token)
    _save("GOOGLE_CLIENT_ID",     creds.client_id)
    _save("GOOGLE_CLIENT_SECRET", creds.client_secret)
    print("  Credenciais OAuth salvas.\n")

    headers = {"Authorization": f"Bearer {creds.token}"}

    # --- Passo 2: Listar contas ---
    print("[2/3] Buscando contas do Google Business Profile...")
    resp     = httpx.get(
        "https://mybusinessaccountmanagement.googleapis.com/v1/accounts",
        headers=headers, timeout=15,
    )
    accounts = resp.json().get("accounts", [])

    if not accounts:
        print("\nNenhuma conta encontrada.")
        print("Verifique se o perfil esta verificado em business.google.com")
        sys.exit(1)

    print("\nContas encontradas:")
    for i, acc in enumerate(accounts):
        print(f"  [{i}] {acc.get('accountName')} — {acc.get('name')}")

    idx     = int(input("\nQual conta usar? [0]: ").strip() or "0")
    account = accounts[idx]
    _save("GOOGLE_ACCOUNT_NAME", account["name"])
    print()

    # --- Passo 3: Listar locais ---
    print("[3/3] Buscando locais desta conta...")
    resp      = httpx.get(
        f"https://mybusinessbusinessinformation.googleapis.com/v1/{account['name']}/locations",
        headers=headers,
        params={"readMask": "name,title"},
        timeout=15,
    )
    locations = resp.json().get("locations", [])

    if not locations:
        print("\nNenhum local encontrado nesta conta.")
        sys.exit(1)

    print("\nLocais encontrados:")
    for i, loc in enumerate(locations):
        print(f"  [{i}] {loc.get('title')} — {loc.get('name')}")

    idx      = int(input("\nQual local usar? [0]: ").strip() or "0")
    location = locations[idx]

    # Converte para o formato esperado pelo GMB API v4: accounts/X/locations/Y
    raw_name  = location["name"]            # locations/Y
    loc_v4    = f"{account['name']}/{raw_name}"   # accounts/X/locations/Y
    _save("GOOGLE_LOCATION_NAME", loc_v4)

    print("\n" + "=" * 50)
    print("Setup concluido! Variaveis salvas no .env:")
    print("  GOOGLE_REFRESH_TOKEN, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET")
    print("  GOOGLE_ACCOUNT_NAME, GOOGLE_LOCATION_NAME")
    print("\nProximo passo: complete o restante do .env e execute:")
    print("  uvicorn src.main:app --host 0.0.0.0 --port 8000\n")


if __name__ == "__main__":
    main()
