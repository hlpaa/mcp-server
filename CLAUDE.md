# MCP Server

MCP server local em Python que expõe ferramentas de monitoramento do sistema e consulta a banco de dados.

## Stack

- Python 3.12 + `mcp==2.1.1` (`MCPServer`)
- Dependências: `psutil`, `sqlite3` (stdlib), `re` (stdlib)
- Venv: `.venv/` — sempre ativar antes de rodar

## Como rodar

```bash
source .venv/bin/activate
python server.py
```

O servidor roda via stdio (padrão MCP).

## Adicionar uma nova ferramenta

Toda ferramenta é uma função decorada com `@mcp.tool()` em `server.py`:

```python
@mcp.tool()
def nome_da_ferramenta(param: tipo = default) -> dict:
    """Descrição curta em português."""
    ...
```

- Retorne `dict` ou `list[dict]`
- Docstring vira a descrição da tool no MCP
- Não há arquivo separado — tudo vai em `server.py`

## Ferramentas existentes

| Tool | Descrição |
|------|-----------|
| `get_cpu_usage(interval_seconds)` | Uso de CPU total e por núcleo |
| `list_processes(limit, sort_by)` | Processos ordenados por CPU ou memória |
| `get_disk_usage(path)` | Uso de disco de um caminho |
| `query_database(sql, db_path)` | Executa SELECT em um banco SQLite |

## Dependências

Arquivo de dependências: `requirements.text` (atenção ao nome).

Instalar:
```bash
pip install -r requirements.text
```

## Segurança

`query_database` aceita apenas queries SELECT — qualquer outra instrução é bloqueada via regex antes de chegar ao SQLite.
