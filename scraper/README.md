# Agenty — Google Maps Scraper + Notion CRM

Pipeline de prospecção: raspa o Google Maps → analisa potencial → cadastra no Notion com script de abordagem pronto.

## Instalação

```bash
cd scraper
pip install -r requirements.txt
playwright install chromium
```

## Configuração do Notion

### 1. Crie uma integração no Notion
- Acesse https://www.notion.so/my-integrations
- Crie uma integração com permissão de leitura/escrita
- Copie o **Internal Integration Token**

### 2. Crie o banco de dados automaticamente

```bash
# Abra a página no Notion onde quer criar o banco e copie o ID da URL
# Ex: notion.so/SEU-WORKSPACE/MEU-PAGE-ID → use MEU-PAGE-ID
python crm_sync.py --setup --page-id SEU_PAGE_ID --api-key seu_token
```

### 3. Configure as variáveis de ambiente

```bash
# Windows (PowerShell)
$env:NOTION_API_KEY = "secret_..."
$env:NOTION_DATABASE_ID = "banco-id-aqui"

# Ou crie um arquivo .env e use python-dotenv
```

> **Importante:** Compartilhe o banco de dados com a sua integração no Notion (botão "Share" → adicione a integração).

## Uso

### Busca única
```bash
python maps_scraper.py --query "restaurante Curitiba" --max 30
```

### Rodar todas as queries do config.py
```bash
python maps_scraper.py --all --max 20
```

### Sem sincronizar com o Notion (só CSV/JSON)
```bash
python maps_scraper.py --all --no-crm
```

### Modo visível (abre o navegador — útil para debug)
```bash
python maps_scraper.py --query "clínica Curitiba" --visible
```

## Output

Os arquivos são salvos em `output/`:
- `leads.json` — dados brutos de todos os negócios
- `leads.csv` — leads classificados com score e script de abordagem

## Adicionar novos segmentos

Edite `config.py`:
```python
SEARCH_QUERIES = [
    "seu segmento Curitiba",
    ...
]
```

## Estrutura do Lead no Notion

| Campo | Descrição |
|-------|-----------|
| Nome do Negócio | Nome extraído do Maps |
| Status | Novo / A contatar / Em negociação / Cliente / Descartado |
| Prioridade | Alta / Média / Baixa (calculada pelo score) |
| Score | 0-100 (baseado em dores e oportunidades) |
| Avaliação Google | Nota no Maps (ex: 4.2) |
| Nº Avaliações | Quantidade de avaliações |
| Telefone | Número extraído do Maps |
| Site | URL do site (se tiver) |
| Dores Identificadas | Lista das dores identificadas |
| Oportunidades | Soluções de IA aplicáveis |
| Script de Abordagem | Script personalizado para ligar |
| Tem Site | Checkbox |
| Responde Avaliações | Checkbox |
