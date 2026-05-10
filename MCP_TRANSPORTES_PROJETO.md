# MCP-Transportes: Servidor MCP para Transporte Aduaneiro e CT-e

## Integração com Bytex AgentOS via Model Context Protocol

---

## 1. Visão Geral

### 1.1 Objetivo

Criar um servidor **MCP (Model Context Protocol)** dedicado a dados de **transporte aduaneiro e CT-e (Conhecimento de Transporte Eletrônico)** brasileiro, hospedado na mesma VPS Contabo dos servidores MCP-NFe e MCP-ComexStat, permitindo que os agentes do Bytex AgentOS consultem, analisem e cruzem informações sobre **transportadoras, volumes, cargas, tomadores e modais**.

### 1.2 Problema que Resolve

O agente poderá responder perguntas como:

- "Quantos containers a transportadora X levou este mês para Sadia?"
- "Qual o volume total de carga que a transportadora Y transportou em 2025?"
- "Para quais clientes a transportadora Z mais entrega?"
- "Comparativo de volumes entre transportadoras no modal rodoviário"
- "Qual a média de peso por CT-e da transportadora W?"

### 1.3 Arquitetura (Servidor Único)

```
VPS Contabo (mesmo servidor)
├── mcp-nfe (porta 8000)         → NF-e, DANFE
├── mcp-comexstat (porta 8001)   → Comércio exterior
└── mcp-transportes (porta 8002) → CT-e, transportadoras ← NOVO
     │
     ├── Webmania CT-e API → consulta CT-e (pago, R$199+/mês)
     ├── Meu Danfe CT-e    → consulta CT-e por chave (R$0,03/consulta)
     └── [Futuro] LogAPI   → tracking transportadoras (R$2.000+/mês)
```

---

## 2. O que é o CT-e?

O **CT-e (Conhecimento de Transporte Eletrônico)** é o documento fiscal digital que acompanha toda prestação de serviço de transporte no Brasil. Instituído pelo Ajuste SINIEF 09/2007, ele substitui os antigos conhecimentos de transporte em papel.

### 2.1 Dados Contidos em um CT-e

| Campo | Descrição | Exemplo |
|---|---|---|
| **Chave de acesso** | Identificador único de 44 dígitos | 35200612345678901234567890123456789012345678 |
| **Transportadora** | CNPJ + Razão Social | 12.345.678/0001-90 - Transportadora X Ltda |
| **Tomador** | Quem contratou o frete | Sadia S.A. (CNPJ: ...) |
| **Remetente** | Quem enviou a mercadoria | Frigorífico Y |
| **Destinatário** | Quem recebeu | Supermercado Z |
| **Produto** | NCM, descrição, peso, volumes | Carne bovina congelada - NCM 02023000 |
| **Modal** | Rodoviário, Aéreo, Marítimo, Ferroviário, Dutoviário | Rodoviário |
| **Valor do frete** | Valor do serviço | R$ 5.000,00 |
| **Peso bruto** | Peso total da carga | 25.000 kg |
| **Quantidade** | Volumes transportados | 100 containers |
| **Municípios** | Origem e destino | São Paulo → Recife |
| **CFOP** | Código Fiscal | 6351 |

---

## 3. Fontes de Dados

### 3.1 Webmania CT-e (Primeira opção — Paga)

| Atributo | Detalhe |
|---|---|
| **URL** | `https://webmania.com.br/docs/rest-api-nfe/#cte` |
| **Preço** | R$ 199+/mês (plano Emissor) |
| **Cobertura** | Nacional |
| **Dados** | Emissão, consulta, cancelamento, inutilização, CC-e, manifestação, download XML/PDF, status SEFAZ |
| **Auth** | 4 chaves (Consumer Key, Consumer Secret, Access Token, Access Token Secret) |
| **Tipo** | REST API |
| **SDKs** | Python, Node.js, PHP, Java, C#, Go, Ruby |
| **Indicado para** | Consulta de CT-e de terceiros + emissão própria |

**Endpoints Relevantes:**
- `GET /cte/{chave}` — Consultar CT-e por chave
- `GET /cte/{chave}/pdf` — Download do PDF do CT-e
- `GET /cte/{chave}/xml` — Download do XML do CT-e

---

### 3.2 Meu Danfe CT-e (Segunda opção — Quase Grátis)

| Atributo | Detalhe |
|---|---|
| **URL** | `https://meudanfe.com.br/api` |
| **Preço** | **Gratuito** para geração de DACTE. **R$ 0,03/consulta** para busca de CT-e por chave |
| **Cobertura** | CT-e consultado na base interna (não na Receita, exceto quando necessário) |
| **Dados** | Geração de DACTE PDF, download de XML, consulta de CT-e por chave |
| **Auth** | API Key via cadastro |
| **Tipo** | REST API |
| **Indicado para** | Consulta eventual de CT-e + geração de DACTE a baixo custo |

---

### 3.3 LogAPI ⚠️ (Alternativa Futura — Fora do Escopo Atual)

| Atributo | Detalhe |
|---|---|
| **URL** | `https://www.logapi.com.br/` |
| **Preço** | R$ 2.000+/mês (fora do orçamento atual) |
| **Cobertura** | Rastreamento de 20+ transportadoras |
| **Status** | **Em radar** — alternativa futura quando houver orçamento |

---

## 4. Ferramentas MCP (Tools)

### 4.1 Ferramentas de Consulta CT-e

| Tool | Descrição | Fonte |
|---|---|---|
| `consultar_cte_por_chave(chave)` | Dados completos de um CT-e pela chave de 44 dígitos | Webmania / Meu Danfe |
| `consultar_cte_por_periodo(inicio, fim)` | Lista CT-e emitidos em um período | Webmania |
| `consultar_cte_por_transportadora(cnpj, periodo)` | CT-e de uma transportadora específica | Webmania |
| `consultar_cte_por_tomador(cnpj, periodo)` | CT-e contratados por um tomador específico | Webmania |
| `gerar_dacte(chave)` | Gera PDF do DACTE (Documento Auxiliar) | Meu Danfe |

### 4.2 Ferramentas de Análise por Transportadora

| Tool | Descrição |
|---|---|
| `volumes_por_transportadora(cnpj, periodo)` | Total de volumes, peso e valor por transportadora |
| `clientes_por_transportadora(cnpj, periodo)` | Lista de tomadores/clientes e seus volumes |
| `ranking_transportadoras(periodo, limite)` | Transportadoras que mais transportaram |
| `comparativo_transportadoras(cnpjs, periodo)` | Comparativo entre transportadoras |
| `media_peso_por_cte(cnpj, periodo)` | Peso médio por CT-e de uma transportadora |

### 4.3 Ferramentas de Análise por Tomador (Cliente)

| Tool | Descrição |
|---|---|
| `transportadoras_por_cliente(cnpj, periodo)` | Quais transportadoras um cliente mais usa |
| `volumes_por_cliente(cnpj, periodo)` | Total de volumes transportados para um cliente |
| `frota_por_cliente(cnpj, periodo)` | Distribuição de cargas por transportadora para um cliente |

### 4.4 Ferramentas de Análise por Modal

| Tool | Descrição |
|---|---|
| `consultar_por_modal(modal, periodo)` | CT-e por modal (rodoviário, aéreo, marítimo) |
| `comparativo_modais(periodo)` | Comparação de volumes entre modais |
| `transportadoras_por_modal(modal)` | Transportadoras que operam em cada modal |

### 4.5 Ferramentas de Cross-Reference (ComexStat + CT-e)

| Tool | Descrição | APIs envolvidas |
|---|---|---|
| `produtos_mais_transportados(ncm, periodo)` | Transporte de um produto específico | ComexStat + CT-e |
| `corredor_logistico(uf_origem, uf_destino)` | Fluxo de cargas entre estados | CT-e |
| `transportadoras_por_produto(ncm)` | Quem mais transporta um tipo de produto | CT-e |

---

## 5. Exemplos de Uso com Agentes IA

### Exemplo 1: Volumes por Transportadora

**Usuário:** "Quantos containers a transportadora X levou este mês?"

O agente chama:
```python
dados = volumes_por_transportadora(
    cnpj="12.345.678/0001-90",
    periodo={"from": "2026-05-01", "to": "2026-05-10"}
)
```

**Resposta do agente:**
```
📦 Transportadora X Ltda
   Período: 01/05/2026 a 10/05/2026
   
   Total de CT-e: 47
   Peso total: 1.234.500 kg
   Volumes: 450 containers
   Valor total fretes: R$ 587.230,00
   
   Top 3 clientes:
   1. Sadia S.A. — 120 containers (27%)
   2. Seara Alimentos — 85 containers (19%)
   3. JBS S.A. — 62 containers (14%)
```

### Exemplo 2: Clientes por Transportadora

**Usuário:** "Para quais clientes a transportadora Y mais entrega?"

O agente chama:
```python
clientes = clientes_por_transportadora(
    cnpj="98.765.432/0001-10",
    periodo={"from": "2026-01-01", "to": "2026-12-31"}
)
```

**Resposta do agente:**
```
🏢 Clientes da Transportadora Y em 2026:
1. Ambev — 1.200 CT-e (R$ 2.4M em fretes)
2. Nestlé — 890 CT-e (R$ 1.8M)
3. BRF — 650 CT-e (R$ 1.3M)
...
Total: 4.500 CT-e emitidos no ano
```

### Exemplo 3: Cross-Reference ComexStat + CT-e

**Usuário:** "Qual a relação entre exportação de carnes e o transporte rodoviário?"

O agente chama:
```python
# 1. Exportação de carnes
exp = consultar_exportacao(ano=2025, ncm="02")
# 2. Transporte rodoviário de carnes
transp = consultar_por_modal(modal="rodoviario", periodo=2025)
```

---

## 6. Implementação do Servidor MCP

### 6.1 Estrutura de Diretórios

```
/opt/mcp-transportes/
├── .env                          # Chaves das APIs
├── requirements.txt
├── server.py                     # Servidor MCP principal
├── mcp_transportes/
│   ├── __init__.py
│   ├── api_webmania.py           # Cliente Webmania CT-e
│   ├── api_meudanfe.py           # Cliente Meu Danfe CT-e
│   ├── tools_cte.py              # Tools de consulta CT-e
│   ├── tools_transportadoras.py  # Tools de análise por transportadora
│   ├── tools_clientes.py         # Tools de análise por cliente
│   ├── tools_modais.py           # Tools de análise por modal
│   └── tools_cross.py            # Tools cross-reference
└── systemd/
    └── mcp-transportes.service
```

### 6.2 server.py

```python
from fastmcp import FastMCP
from mcp_transportes.tools_cte import register_cte_tools
from mcp_transportes.tools_transportadoras import register_transportadoras_tools
from mcp_transportes.tools_clientes import register_clientes_tools
from mcp_transportes.tools_modais import register_modais_tools
from mcp_transportes.tools_cross import register_cross_tools

mcp = FastMCP("mcp-transportes")

register_cte_tools(mcp)
register_transportadoras_tools(mcp)
register_clientes_tools(mcp)
register_modais_tools(mcp)
register_cross_tools(mcp)

if __name__ == "__main__":
    mcp.run(transport="sse", host="0.0.0.0", port=8002)
```

### 6.3 api_webmania.py — Cliente Webmania CT-e

```python
import httpx
import os

CONSUMER_KEY = os.getenv("WEBMANIA_CONSUMER_KEY")
CONSUMER_SECRET = os.getenv("WEBMANIA_CONSUMER_SECRET")
ACCESS_TOKEN = os.getenv("WEBMANIA_ACCESS_TOKEN")
TOKEN_SECRET = os.getenv("WEBMANIA_TOKEN_SECRET")
BASE_URL = "https://webmaniabr.com/api/1/cte"


class WebmaniaCTeClient:

    def __init__(self):
        self.headers = {
            "X-Consumer-Key": CONSUMER_KEY,
            "X-Consumer-Secret": CONSUMER_SECRET,
            "X-Access-Token": ACCESS_TOKEN,
            "X-Access-Token-Secret": TOKEN_SECRET,
            "Content-Type": "application/json",
        }
        self.client = httpx.AsyncClient(headers=self.headers, timeout=30)

    async def consultar_cte(self, chave: str) -> dict:
        """Consulta um CT-e pela chave de acesso."""
        resp = await self.client.get(f"{BASE_URL}/{chave}/")
        resp.raise_for_status()
        return resp.json()

    async def listar_cte(self, pagina: int = 1) -> dict:
        """Lista CT-e emitidos."""
        resp = await self.client.get(f"{BASE_URL}/?pagina={pagina}")
        resp.raise_for_status()
        return resp.json()

    async def close(self):
        await self.client.aclose()
```

### 6.4 tools_transportadoras.py — Exemplo de Tool

```python

def register_transportadoras_tools(mcp: FastMCP):

    @mcp.tool()
    async def volumes_por_transportadora(
        cnpj: str,
        ano: int,
        mes_inicio: int = 1,
        mes_fim: int = 12
    ) -> dict:
        """
        Retorna volumes totais transportados por uma transportadora em um período.

        Args:
            cnpj: CNPJ da transportadora (apenas números)
            ano: Ano desejado
            mes_inicio: Mês inicial (1-12)
            mes_fim: Mês final (1-12)
        """
        from .api_webmania import WebmaniaCTeClient
        client = WebmaniaCTeClient()
        try:
            # Lógica de consulta agregada
            result = await client.listar_cte()
            # Processar e agrupar por tomador...
            return {
                "transportadora": cnpj,
                "periodo": f"{mes_inicio}/{ano} a {mes_fim}/{ano}",
                "total_cte": 0,
                "peso_total_kg": 0,
                "volumes": 0,
                "valor_total_fretes": 0,
                "clientes": [],
            }
        finally:
            await client.close()

    @mcp.tool()
    async def ranking_transportadoras(ano: int, limite: int = 10) -> list:
        """
        Ranking das transportadoras que mais transportaram no ano.

        Args:
            ano: Ano desejado
            limite: Quantidade de transportadoras no ranking
        """
        # Lógica de ranking
        return []
```

---

## 7. Integração com Bytex AgentOS

### 7.1 Configuração do Agente

```python
MCP_SERVERS = [
    {"name": "mcp-nfe", "url": "https://mcp.bytex.com.br/nfe/sse", "transport": "sse"},
    {"name": "mcp-comexstat", "url": "https://mcp.bytex.com.br/comexstat/sse", "transport": "sse"},
    {"name": "mcp-transportes", "url": "https://mcp.bytex.com.br/transportes/sse", "transport": "sse"},
]
```

### 7.2 Exemplos de Prompts

| Pergunta | Tools |
|---|---|
| "Volume de carga da Transportadora X em 2025" | `volumes_por_transportadora()` |
| "Quanto a Sadia gastou em fretes no último trimestre?" | `transportadoras_por_cliente()` + `volumes_por_cliente()` |
| "Ranking de transportadoras rodoviárias" | `ranking_transportadoras()` + `transportadoras_por_modal()` |
| "Comparativo de fretes entre Sul e Nordeste" | `corredor_logistico()` |
| "Quais transportadoras mais levam carne bovina?" | `transportadoras_por_produto()` + ComexStat |

---

## 8. Custo Mensal

| Item | Custo |
|---|---|
| **VPS Contabo** (compartilhada) | €6,99/mês (já contabilizado) |
| **Webmania CT-e** | R$ 199+/mês (quando contratar) |
| **Meu Danfe CT-e** | R$ 0,03/consulta (uso inicial) |
| **LogAPI** | **R$ 2.000+/mês** ⚠️ Fora do escopo atual — em radar para futuro |

---

## 9. Cronograma

| Fase | O que | Tempo |
|---|---|---|
| **1** | Setup VPS + estrutura (compartilhado) | 1 hora |
| **2** | Desenvolver cliente Webmania CT-e | 2 horas |
| **3** | Tools de consulta CT-e | 2 horas |
| **4** | Tools de análise transportadoras + clientes | 2 horas |
| **5** | Tools cross-reference com ComexStat | 1 hora |
| **6** | Testes + deploy | 1 hora |
| | **Total** | **~9 horas** |

---

## 10. Observações

### Sobre a LogAPI
A **LogAPI** (R$ 2.000+/mês) é uma plataforma premium de rastreamento que cobre **20+ transportadoras**. Foi **deliberadamente excluída** do escopo atual por questões de custo, mas permanece no **radar** como alternativa futura quando o orçamento permitir. Ela adicionaria a capacidade de **rastreamento em tempo real** de entregas, algo que as APIs de CT-e não oferecem.

### Dependência entre os MCPs
- **mcp-nfe** + **mcp-transportes**: complementares (NF-e do produto + CT-e do transporte)
- **mcp-comexstat** + **mcp-transportes**: complementares (exportação + transporte aduaneiro)
- Os três podem ser consultados simultaneamente pelo mesmo agente para análises complexas

---

*Documento gerado em 10/05/2026 — Bytex AgentOS*
