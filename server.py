from mcp.server.mcpserver import MCPServer
from dotenv import load_dotenv
import psutil
import os
import sqlite3
import re
import requests

load_dotenv()

mcp = MCPServer("mcp-server")


@mcp.tool()
def get_cpu_usage(interval_seconds: float = 1.0) -> dict:
    """Retorna uso de CPU atual, total e por núcleo."""
    total = psutil.cpu_percent(interval=interval_seconds)
    per_core = psutil.cpu_percent(interval=interval_seconds, percpu=True)
    return {
        "total_percent": total,
        "per_core": per_core
    }


@mcp.tool()
def list_processes(limit: int = 10, sort_by: str = "cpu") -> list[dict]:
     """Lista os processos do sistema ordenados por CPU ou memória."""
     procs = []
     for p in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"]):
         try:
             info = p.info
             procs.append({
                 "pid": info["pid"],
                 "name": info["name"],
                 "cpu_percent": info["cpu_percent"] or 0.0,
                 "mem_percent": round(info["memory_percent"] or 0.0, 2),
             })
         except (psutil.NoSuchProcess, psutil.AccessDenied):
             continue
     key = "mem_percent" if sort_by == "mem" else "cpu_percent"
     return sorted(procs, key=lambda x: x[key], reverse=True)[:limit]

@mcp.tool()
def get_disk_usage(path: str = "/") -> dict:
     """Retorna uso de disco para um caminho (padrão: raiz)."""
     st = os.statvfs(path)
     total = st.f_frsize * st.f_blocks
     free  = st.f_frsize * st.f_bfree
     used  = total - free
     return {
         "total_gb":    round(total / 1e9, 2),
         "used_gb":     round(used  / 1e9, 2),
         "free_gb":     round(free  / 1e9, 2),
         "percent_used": round(used / total * 100, 1),
     }

@mcp.tool()
def query_database(sql: str, db_path: str = "loja.db") -> dict:
     """Executa uma query SELECT em um banco SQLite e retorna as linhas."""
     if not re.match(r"^\s*SELECT", sql, re.IGNORECASE):
         return {"error": "Apenas queries SELECT são permitidas"}
     try:
         conn = sqlite3.connect(db_path)
         conn.row_factory = sqlite3.Row
         cursor = conn.execute(sql)
         rows = [dict(row) for row in cursor.fetchall()]
         return {"rows": rows, "count": len(rows)}
     except sqlite3.Error as e:
         return {"error": str(e)}
     finally:
         conn.close()


@mcp.tool()                                                                                                                                                                           
def search_github_issues(query: str, repo: str = None, max_results: int = 20) -> dict:                                                                                                      
      """Busca issues no GitHub usando a API de search."""                                                                                                                                    
      token = os.environ.get("GITHUB_TOKEN")                                                                                                                                                  
      if not token:                                                                                                                                                                           
          return {"error": "Variável de ambiente GITHUB_TOKEN não está definida"}

      parts = [query]
      if "is:issue" not in query and "is:pull-request" not in query:
          parts.append("is:issue")
      if repo:
          parts.append(f"repo:{repo}")
      q = " ".join(parts)

      headers = {
          "Authorization": f"Bearer {token}",
          "Accept": "application/vnd.github+json",
      }                                                                                                                                                                                       
      params = {"q": q, "per_page": min(max_results, 100)}
                                                                                                                                                                                              
      try:        
          resp = requests.get(
              "https://api.github.com/search/issues",
              headers=headers,
              params=params,
              timeout=10,
          )
      except requests.exceptions.RequestException as e:
          return {"error": f"Falha na requisição: {e}"}                                                                                                                                       
                                                                                                                                                                                              
      if resp.status_code != 200:                                                                                                                                                             
          return {"error": f"GitHub retornou {resp.status_code}: {resp.text}"}                                                                                                                
                  
      data = resp.json()
      issues = [
          {
              "number": i["number"],
              "title": i["title"],
              "state": i["state"],
              "labels": [l["name"] for l in i.get("labels", [])],                                                                                                                             
              "assignee": (i.get("assignee") or {}).get("login"),                                                                                                                             
              "url": i["html_url"],                                                                                                                                                           
          }                                                                                                                                                                                   
          for i in data.get("items", [])
      ]
      return {"issues": issues, "count": len(issues)}

if __name__ == "__main__":
    mcp.run()

