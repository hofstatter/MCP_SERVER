# MCP-ComexStat: Servidor MCP para Comércio Exterior Brasileiro

## Integração com Bytex AgentOS via Model Context Protocol

---

## 1. Visão Geral

### 1.1 Objetivo

Criar um servidor **MCP (Model Context Protocol)** dedicado aos dados de comércio exterior brasileiro, hospedado em VPS Contabo, que permita aos agentes do Bytex AgentOS consultar, analisar e cruzar informações de **exportação, importação, modais, produtos e países** com base nos dados oficiais do governo federal (ComexStat/SECEX/MDIC).

### 1.2 Dados Disponíveis

| Fonte | Dados | Cobertura | Custo |
|---|---|---|---|
| **ComexStat API** (oficial MDIC) | Exportação, importação, NCM, países, UF, municípios, modais | 1989-2026 (37 anos) | **Gratuito** |
| **Bulk CSV** (balança comercial) | Dados brutos completos para download | 1997-2026 | **Gratuito** |

### 1.3 Arquitetura

```
Bytex AgentOS
  └── Agente IA (Claude/DeepSeek/Groq)
       └── MCP Client (conexão via SSE)
            │
            │ HTTPS / TLS
            │
    VPS Contabo
    └── Nginx (SSL termination + proxy reverso)
         └── MCP Server (FastMCP + Python)
              │
              ├── ComexStat API (dados oficiais)
              │   ├── Consultar exportação/importação
              │   ├── Produtos por NCM/SH/NBM
              │   ├── Países parceiros comerciais
              │   ├── Modais (aéreo, marítimo, rodoviário)
              │   ├── Municípios/UF
              │   └── Períodos mensais/anuais
              │
              └── Cache local + tabelas auxiliares
                  ├── NCM (10.000+ códigos)
                  ├── Países (~230)
                  ├── Estados + municípios
                  └── Modais de transporte
```

---

## 2. API ComexStat — Documentação Completa

### 2.1 Base URL

```
https://api-comexstat.mdic.gov.br
```

**Sem autenticação. Sem token. Sem rate limit.** API pública e gratuita.

### 2.2 Endpoints Disponíveis

| Endpoint | Método | Descrição |
|---|---|---|
| `/general` | **POST** | Consulta principal de exportação/importação |
| `/cities` | **POST** | Consulta por município |
| `/historical-data` | **POST** | Dados históricos (1989-1996) |
| `/general/dates/updated` | GET | Última atualização dos dados |
| `/general/dates/years` | GET | Ano mínimo e máximo disponível |
| `/general/filters` | GET | Dimensões de filtro disponíveis |
| `/general/filters/{filter}` | GET | Valores de um filtro específico |
| `/general/details` | GET | Campos de detalhamento/agrupamento |
| `/general/metrics` | GET | Métricas disponíveis |
| `/tables/uf` | GET | Lista de estados |
| `/tables/uf/{id}` | GET | Detalhes de um estado |
| `/tables/cities` | GET | Lista de municípios |
| `/tables/cities/{id}` | GET | Detalhes de um município |
| `/tables/countries` | GET | Lista de países |
| `/tables/countries/{id}` | GET | Detalhes de um país |
| `/tables/economic-blocks` | GET | Blocos econômicos |
| `/tables/hs` | GET | Classificações SH (NCM) |
| `/tables/nbm` | GET | NBM (Nomenclatura Brasileira) |
| `/tables/nbm/{id}` | GET | Detalhes de NBM |

### 2.3 Formato da Consulta Principal (`POST /general`)

```json
{
  "flow": "export",
  "monthDetail": true,
  "period": {
    "from": "2024-01",
    "to": "2025-12"
  },
  "filters": [
    { "filter": "country", "values": [105, 107] },
    { "filter": "state", "values": [26, 13] },
    { "filter": "via", "values": [1, 2] }
  ],
  "details": ["country", "state", "ncm"],
  "metrics": ["metricFOB", "metricKG"]
}
```

### 2.4 Dimensões de Filtro (disponíveis via `/general/filters`)

| Filter ID | Descrição | Exemplo de valores |
|---|---|---|
| `country` | País de destino/origem | 105 = Brasil, 107 = Argentina |
| `state` | Unidade Federativa | 26 = SP, 13 = RJ |
| `economicBlock` | Bloco econômico | Mercosul, União Europeia |
| `via` | Modal de transporte | 1 = Marítimo, 2 = Rodoviário, 3 = Aéreo |
| `urf` | Unidade da Receita Federal | Código da aduana |
| `ncm` | NCM 8 dígitos | 84713000 = Notebook |
| `subHeading` | SH 6 dígitos | Agrupamento internacional |
| `heading` | SH 4 dígitos | Categoria de produto |
| `chapter` | SH 2 dígitos | Capítulo (ex: 84 = Máquinas) |
| `section` | Seção SH | Seção XVI = Máquinas e Aparelhos |
| `BECLevel3/2/1` | CGCE | Classificação por uso econômico |
| `SITCBasicHeading/SubGroup/Group/Division/Section` | CUCI | Classificação de comércio internacional |

### 2.5 Métricas Disponíveis

| Métrica | Descrição | Export | Import |
|---|---|---|---|
| `metricFOB` | Valor US$ FOB | ✅ | ✅ |
| `metricKG` | Quilograma líquido | ✅ | ✅ |
| `metricStatistic` | Quantidade estatística | ✅ | ✅ |
| `metricFreight` | Valor do frete US$ | ❌ | ✅ |
| `metricInsurance` | Valor do seguro US$ | ❌ | ✅ |
| `metricCIF` | Valor US$ CIF | ❌ | ✅ |

### 2.6 Cobertura

| Período | Anos | Endpoint |
|---|---|---|
| Dados principais | 1997-2026 | `/general` |
| Dados históricos | 1989-1996 | `/historical-data` |
| Última atualização | 07/05/2026 | Dados até abril/2026 |

---

## 3. Ferramentas MCP (Tools)

### 3.1 Ferramentas de Consulta Principal

| Tool | Descrição |
|---|---|
| `consultar_exportacao(ano, mes, ncm)` | Dados de exportação por produto/período |
| `consultar_importacao(ano, mes, ncm)` | Dados de importação por produto/período |
| `consultar_por_pais(pais, ano, flow)` | Exportação/importação com parceiro comercial |
| `consultar_por_estado(uf, ano, flow)` | Dados de comércio por estado |
| `consultar_por_modal(modal, ano)` | Dados por modal (aéreo, marítimo, rodoviário) |
| `consultar_por_municipio(codigo_ibge, ano)` | Dados por município |
| `consultar_periodo(ano_inicio, ano_fim, flow)` | Série histórica de um período |

### 3.2 Ferramentas de Produto (NCM/SH)

| Tool | Descrição |
|---|---|
| `listar_ncm(codigo, descricao)` | Buscar códigos NCM por número ou descrição |
| `top_produtos_exportados(ano, limite)` | Produtos mais exportados no ano |
| `top_produtos_importados(ano, limite)` | Produtos mais importados no ano |
| `consultar_produto_por_ncm(ncm, ano)` | Dados completos de exportação/importação de um NCM |
| `comparar_exportacao_importacao(ncm, ano)` | Comparação exp vs imp de um produto |
| `produtos_por_secao(secao_sh, ano)` | Produtos de uma seção SH |

### 3.3 Ferramentas de País e Bloco

| Tool | Descrição |
|---|---|
| `listar_paises(termo)` | Buscar países por nome ou código |
| `top_parceiros_exportacao(ano, limite)` | Maiores compradores do Brasil |
| `top_parceiros_importacao(ano, limite)` | Maiores vendedores para o Brasil |
| `consultar_corrente_comercial(pais, ano)` | Exportação + importação com um país |
| `consultar_por_bloco(bloco, ano)` | Dados por bloco econômico (Mercosul, UE, etc.) |

### 3.4 Ferramentas de Modal (Transporte)

| Tool | Descrição |
|---|---|
| `listar_modais()` | Lista todos os modais de transporte disponíveis |
| `consultar_por_modal(modal, ano, flow)` | Dados de comércio por modal |
| `comparar_modais(ano, flow)` | Comparação entre modais para um ano |
| `modais_por_produto(ncm, ano)` | Modais utilizados para um produto específico |

### 3.5 Ferramentas de Análise e Insight

| Tool | Descrição |
|---|---|
| `analisar_tendencia(ncm, anos)` | Tendência de exportação/importação de um produto |
| `balanca_comercial(ano)` | Saldo da balança comercial (exportação - importação) |
| `produtos_com_alta(ano, variacao)` | Produtos com maior crescimento nas exportações |
| `produtos_com_baixa(ano, variacao)` | Produtos com maior queda nas exportações |
| `resumo_anual(ano)` | Resumo completo do comércio exterior no ano |
| `ranking_estados(ano, flow)` | Ranking dos estados que mais exportam/importam |

### 3.6 Ferramentas de Metadados

| Tool | Descrição |
|---|---|
| `ultima_atualizacao()` | Data da última atualização dos dados |
| `anos_disponiveis()` | Intervalo de anos disponível para consulta |
| `metricas_disponiveis()` | Lista de métricas que podem ser consultadas |
| `dimensoes_disponiveis()` | Lista de dimensões de filtro |

---

## 4. Exemplos de Uso com Agentes IA

### Exemplo 1: "Quais foram os 10 produtos mais exportados pelo Brasil em 2024?"

O agente chama:
```
top_produtos_exportados(ano=2024, limite=10)
```

Retorna:
```
1. Minério de ferro (NCM 26011100) — US$ 28,5 bilhões
2. Petróleo bruto (NCM 27090010) — US$ 24,1 bilhões
3. Soja (NCM 12019000) — US$ 22,3 bilhões
...
```

### Exemplo 2: "Quanto o Brasil exportou de carne bovina para a China em 2024?"

O agente chama:
```python
dados = consultar_exportacao(
    ano=2024,
    ncm="02013000",  # Carne bovina congelada
    pais="160"       # China
)
```

### Exemplo 3: "Qual modal de transporte é mais usado para exportar para a Europa?"

O agente chama:
```python
modais = consultar_por_pais(
    pais=175,     # Alemanha
    ano=2024,
    flow="export"
)
# Retorna breakdown por modal (marítimo ~85%, aéreo ~12%, etc.)
```

### Exemplo 4: "Faça um resumo completo do comércio exterior brasileiro em 2025"

O agente chama:
```python
resumo = resumo_anual(ano=2025)
# Retorna: balança comercial, top 5 produtos exportados,
# top 5 parceiros, participação por estado, modais
```

---

## 5. Implementação do Servidor MCP

### 5.1 Estrutura de Diretórios

```
/opt/mcp-comexstat/
├── .env
├── requirements.txt
├── server.py                    # Servidor MCP principal
├── mcp_comexstat/
│   ├── __init__.py
│   ├── api.py                   # Cliente da API ComexStat
│   ├── tools_consulta.py        # Tools de consulta principal
│   ├── tools_produtos.py        # Tools de produtos NCM
│   ├── tools_paises.py          # Tools de países e blocos
│   ├── tools_modais.py          # Tools de modais
│   ├── tools_analise.py         # Tools de análise e insight
│   ├── tools_meta.py            # Tools de metadados
│   └── cache.py                 # Cache local de tabelas
└── systemd/
    └── mcp-comexstat.service
```

### 5.2 `server.py` — Servidor Principal

```python
from fastmcp import FastMCP
from mcp_comexstat.tools_consulta import register_consulta_tools
from mcp_comexstat.tools_produtos import register_produtos_tools
from mcp_comexstat.tools_paises import register_paises_tools
from mcp_comexstat.tools_modais import register_modais_tools
from mcp_comexstat.tools_analise import register_analise_tools
from mcp_comexstat.tools_meta import register_meta_tools

mcp = FastMCP("mcp-comexstat")

register_consulta_tools(mcp)
register_produtos_tools(mcp)
register_paises_tools(mcp)
register_modais_tools(mcp)
register_analise_tools(mcp)
register_meta_tools(mcp)

if __name__ == "__main__":
    mcp.run(transport="sse", host="0.0.0.0", port=8001)
```

### 5.3 `api.py` — Cliente da API ComexStat

```python
import httpx
from typing import Optional

BASE_URL = "https://api-comexstat.mdic.gov.br"


class ComexStatClient:
    """Cliente para a API oficial do ComexStat."""

    def __init__(self):
        self.client = httpx.AsyncClient(base_url=BASE_URL, timeout=30)

    async def query_general(self, flow: str, period: dict,
                            filters: list = None, details: list = None,
                            metrics: list = None, month_detail: bool = False):
        """Consulta principal de exportação/importação."""
        payload = {
            "flow": flow,
            "monthDetail": month_detail,
            "period": period,
        }
        if filters:
            payload["filters"] = filters
        if details:
            payload["details"] = details
        if metrics:
            payload["metrics"] = metrics
        else:
            payload["metrics"] = ["metricFOB", "metricKG"]

        resp = await self.client.post("/general", json=payload)
        resp.raise_for_status()
        return resp.json()

    async def get_filters(self):
        """Lista dimensões de filtro disponíveis."""
        resp = await self.client.get("/general/filters")
        return resp.json()

    async def get_filter_values(self, filter_id: str):
        """Lista valores de um filtro específico."""
        resp = await self.client.get(f"/general/filters/{filter_id}")
        return resp.json()

    async def get_countries(self):
        """Lista todos os países."""
        resp = await self.client.get("/tables/countries")
        return resp.json()

    async def get_states(self):
        """Lista todos os estados."""
        resp = await self.client.get("/tables/uf")
        return resp.json()

    async def get_metrics(self):
        """Lista métricas disponíveis."""
        resp = await self.client.get("/general/metrics")
        return resp.json()

    async def get_years(self):
        """Anos mínimo e máximo disponíveis."""
        resp = await self.client.get("/general/dates/years")
        return resp.json()

    async def get_last_update(self):
        """Data da última atualização."""
        resp = await self.client.get("/general/dates/updated")
        return resp.json()

    async def close(self):
        await self.client.aclose()
```

### 5.4 `tools_consulta.py` — Exemplo de Tool

```python
from fastmcp import FastMCP
from .api import ComexStatClient


def register_consulta_tools(mcp: FastMCP):

    @mcp.tool()
    async def consultar_exportacao(
        ano: int,
        mes: int = None,
        ncm: str = None,
        pais: int = None,
        estado: int = None
    ) -> dict:
        """
        Consulta dados de exportação do Brasil.

        Args:
            ano: Ano desejado (1997-2026)
            mes: Mês opcional (1-12)
            ncm: Código NCM de 8 dígitos (ex: 84713000)
            pais: Código do país parceiro
            estado: Código da UF
        """
        client = ComexStatClient()
        try:
            period = {"from": f"{ano}-01", "to": f"{ano}-12"}
            filters = []
            details = ["ncm"]

            if mes:
                period = {"from": f"{ano}-{mes:02d}", "to": f"{ano}-{mes:02d}"}
            if ncm:
                filters.append({"filter": "ncm", "values": [ncm]})
            if pais:
                filters.append({"filter": "country", "values": [pais]})
                details.append("country")
            if estado:
                filters.append({"filter": "state", "values": [estado]})
                details.append("state")

            result = await client.query_general(
                flow="export",
                period=period,
                filters=filters if filters else None,
                details=details,
                month_detail=bool(mes),
            )
            return result
        finally:
            await client.close()

    @mcp.tool()
    async def consultar_importacao(
        ano: int,
        mes: int = None,
        ncm: str = None,
        pais: int = None,
        estado: int = None
    ) -> dict:
        """
        Consulta dados de importação do Brasil.

        Args:
            ano: Ano desejado (1997-2026)
            mes: Mês opcional (1-12)
            ncm: Código NCM de 8 dígitos
            pais: Código do país parceiro
            estado: Código da UF
        """
        client = ComexStatClient()
        try:
            period = {"from": f"{ano}-01", "to": f"{ano}-12"}
            filters = []
            details = ["ncm"]

            if mes:
                period = {"from": f"{ano}-{mes:02d}", "to": f"{ano}-{mes:02d}"}
            if ncm:
                filters.append({"filter": "ncm", "values": [ncm]})
            if pais:
                filters.append({"filter": "country", "values": [pais]})
                details.append("country")
            if estado:
                filters.append({"filter": "state", "values": [estado]})
                details.append("state")

            result = await client.query_general(
                flow="import",
                period=period,
                filters=filters if filters else None,
                details=details,
                month_detail=bool(mes),
                metrics=["metricFOB", "metricKG", "metricCIF", "metricFreight"],
            )
            return result
        finally:
            await client.close()
```

### 5.5 `tools_produtos.py` — Exemplo de Tools de Produto

```python

def register_produtos_tools(mcp: FastMCP):

    @mcp.tool()
    async def listar_ncm(codigo: str = None, descricao: str = None) -> list:
        """
        Busca códigos NCM por número ou descrição.

        Args:
            codigo: Código NCM (ex: 8471)
            descricao: Termo para buscar na descrição (ex: 'computador')
        """
        client = ComexStatClient()
        try:
            hs_data = await client.get("/tables/hs")
            results = hs_data.get("data", []) if "data" in hs_data else hs_data

            if codigo:
                results = [r for r in results if codigo in str(r.get("coNcm", ""))]
            if descricao:
                desc = descricao.lower()
                results = [r for r in results if desc in r.get("noNcm", "").lower()]

            return results[:50]
        finally:
            await client.close()

    @mcp.tool()
    async def top_produtos_exportados(ano: int, limite: int = 10) -> list:
        """
        Lista os produtos mais exportados pelo Brasil em um ano.

        Args:
            ano: Ano desejado
            limite: Quantidade de produtos (default 10)
        """
        client = ComexStatClient()
        try:
            result = await client.query_general(
                flow="export",
                period={"from": f"{ano}-01", "to": f"{ano}-12"},
                details=["ncm"],
                month_detail=False,
            )
            linhas = result.get("data", [])
            linhas.sort(key=lambda x: x.get("metricFOB", 0), reverse=True)
            return linhas[:limite]
        finally:
            await client.close()
```

---

## 6. Integração com Bytex AgentOS

### 6.1 Configuração do Agente

O agente no Bytex AgentOS precisa ser configurado para usar o MCP server:

```python
MCP_SERVERS = [
    {
        "name": "mcp-comexstat",
        "url": "https://mcp.bytex.com.br/comexstat/sse",
        "transport": "sse",
    }
]
```

### 6.2 Exemplos de Prompts

| Pergunta do Usuário | Tools que o Agente Chama |
|---|---|
| "Quais produtos o Brasil mais exportou em 2025?" | `top_produtos_exportados(2025)` |
| "Quanto exportamos de soja para a China?" | `consultar_exportacao(ano=2025, ncm=12019000, pais=160)` |
| "Qual estado mais exporta minério de ferro?" | `consultar_por_estado(ncm=26011100, ano=2025)` |
| "Comparativo exportação x importação de carnes" | `comparar_exportacao_importacao(ncm=02)` |
| "Modal mais usado para exportar para os EUA" | `consultar_por_pais(pais=249, ano=2025, flow='export')` |
| "Resumo da balança comercial de 2025" | `resumo_anual(2025)` |
| "Produtos com maior crescimento nas exportações" | `produtos_com_alta(ano=2025, variacao=50)` |
| "Quanto importamos de fertilizantes?" | `consultar_importacao(ano=2025, ncm=31)` |

---

## 7. Custo Mensal Estimado

| Item | Custo |
|---|---|
| **VPS Contabo** (compartilhada com MCP-NFe) | €6.99/mês |
| **API ComexStat** | **Gratuito** |
| **Domínio** (compartilhado) | ~R$ 3,50/mês |
| **Total** | **~€7/mês + R$ 3,50/mês** |

---

## 8. Cronograma de Implementação

| Fase | O que | Tempo |
|---|---|---|
| **1** | Configurar VPS + Python + Nginx (compartilhado) | 1 hora |
| **2** | Desenvolver cliente API ComexStat (`api.py`) | 2 horas |
| **3** | Implementar tools de consulta principal | 2 horas |
| **4** | Implementar tools de produtos, países, modais | 2 horas |
| **5** | Implementar tools de análise e insight | 2 horas |
| **6** | Cache local de tabelas auxiliares | 1 hora |
| **7** | Testar integração com Bytex AgentOS | 1 hora |
| **8** | Documentação + deploy | 1 hora |
| | **Total** | **~12 horas** |

---

## 9. Referências

- [ComexStat API Oficial](https://api-comexstat.mdic.gov.br) — Documentação interativa
- [ComexStat Portal](https://comexstat.mdic.gov.br) — Portal oficial
- [MCP Server ComexStat (TypeScript)](https://github.com/luizzzvictor/mcp-comexstat) — Referência MCP existente
- [ComexstatR (R Package)](https://github.com/jorgeguto/ComexstatR) — Cliente R para a API
- [Dados Abertos MDIC](https://www.gov.br/mdic/pt-br/assuntos/comercio-exterior/estatisticas/base-de-dados-bruta) — Download CSV
- [Manual ComexStat PDF](https://balanca.economia.gov.br/balanca/manual/Manual.pdf) — Documentação completa
- [Smithery - MCP ComexStat](https://smithery.ai) — MCP server publicado
- [FastMCP (Python)](https://github.com/jlowin/fastmcp) — Framework MCP Python
- [Model Context Protocol](https://modelcontextprotocol.io) — Especificação MCP

---

*Documento gerado em 10/05/2026 — Bytex AgentOS*
