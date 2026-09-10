from mcp.server.mcpserver import MCPServer
import psutil
import os

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

if __name__ == "__main__":
    mcp.run()

