# mcp-server

MCP server local em Python que expõe ferramentas de monitoramento do sistema, consulta a banco de dados e busca no GitHub.

## Stack

- Python 3.12 + `mcp==2.1.1`
- Dependências: `psutil`, `requests`, `python-dotenv`, `sqlite3` (stdlib)

## Como rodar

```bash
source .venv/bin/activate
python server.py
```

O servidor roda via stdio (padrão MCP).

## Variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto:

```
GITHUB_TOKEN=ghp_seutoken...
```

## Ferramentas

| Tool | Parâmetros | Descrição |
|------|-----------|-----------|
| `get_cpu_usage` | `interval_seconds=1.0` | Uso de CPU total e por núcleo |
| `list_processes` | `limit=10, sort_by="cpu"` | Processos ordenados por CPU ou memória |
| `get_disk_usage` | `path="/"` | Uso de disco de um caminho |
| `query_database` | `sql, db_path="loja.db"` | Executa SELECT em um banco SQLite |
| `search_github_issues` | `query, repo=None, max_results=20` | Busca issues no GitHub via API |

## Segurança

- `query_database` aceita apenas queries `SELECT` — outras instruções são bloqueadas via regex.
- `search_github_issues` requer `GITHUB_TOKEN` no ambiente. Adiciona `is:issue` automaticamente se não estiver na query.

## Dependências

```bash
pip install -r requirements.text
```
