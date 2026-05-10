# MCP Server — Bytex AgentOS

Conjunto de servidores MCP (Model Context Protocol) para integração de dados brasileiros com agentes de IA.

## Servidores

| Servidor | Porta | Descrição | Status |
|---|---|---|---|
| **B2B** | 8000 | Consulta CNPJ, dados fiscais e empresariais | ✅ Ativo |
| **ComexStat** | 8001 | Comércio exterior brasileiro (exportação/importação) | ✅ Ativo |
| **NF-e** | 8002 *(futuro)* | Nota Fiscal Eletrônica | ⏳ Planejado |
| **Transportes** | 8003 *(futuro)* | CT-e e transportadoras | ⏳ Planejado |

## ComexStat

### Descrição
API oficial do governo brasileiro (SECEX/MDIC) para dados de comércio exterior. **Gratuita, sem autenticação.**

### Dados Disponíveis
- Exportação e importação por NCM (produto), país, estado, município
- Modais: aéreo, marítimo, rodoviário, ferroviário
- Período: 1989-2026 (37 anos)
- Métricas: valor US$ FOB, peso kg, frete, seguro, CIF

### API Base
```
https://api-comexstat.mdic.gov.br
```

### Tools MCP

| Tool | Descrição |
|---|---|
| `ultima_atualizacao()` | Data da última atualização |
| `anos_disponiveis()` | Intervalo de anos |
| `consultar_exportacao()` | Dados de exportação |
| `consultar_importacao()` | Dados de importação |

### Como Conectar

```json
{
  "mcpServers": {
    "comexstat": {
      "url": "https://mcp.bytex.com.br:8001/sse",
      "transport": "sse"
    }
  }
}
```

## Infraestrutura

- **Servidor:** Contabo Cloud VPS
- **OS:** Ubuntu 24.04 LTS
- **CPU:** 6 cores
- **RAM:** 12 GB (7 GB livres)
- **Storage:** 387 GB (280 GB livres)
- **Nginx:** Proxy reverso com rate limiting
- **Python:** 3.12.3 + FastMCP + httpx

## Deploy Rápido

```bash
# Criar ambiente
python3 -m venv venv
source venv/bin/activate
pip install -r comexstat/requirements.txt

# Iniciar servidor
cd comexstat
python3 server.py
```
