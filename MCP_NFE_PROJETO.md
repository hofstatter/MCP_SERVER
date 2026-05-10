# MCP-NFe: Servidor MCP para Nota Fiscal Eletrônica Brasileira

## Integração com Bytex AgentOS via Model Context Protocol

---

## 1. Visão Geral

### 1.1 Objetivo

Criar um servidor **MCP (Model Context Protocol)** dedicado a dados fiscais brasileiros, hospedado em VPS Contabo, que permita aos agentes do Bytex AgentOS consultar, analisar e cruzar informações de **Notas Fiscais Eletrônicas (NF-e)** e dados governamentais para gerar **insights de mercado e produtos**.

### 1.2 Arquitetura

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
              ├── mcp-brasil (70 APIs governamentais)
              │   ├── Portal da Transparência → NFe Executivo Federal
              │   ├── BrasilAPI → CNPJ, CEP, bancos, feriados
              │   ├── BCB → Selic, IPCA, câmbio, PIB
              │   ├── IBGE → geografia, estatísticas, população
              │   ├── SICONFI → dados fiscais municipais/estaduais
              │   ├── Camara/Senado → legislação
              │   └── INPE → clima (opcional)
              │
              └── mcp-nfe (custom)
                  ├── Meu Danfe → consulta NF-e por chave (R$0,03)
                  ├── Serpro → consulta oficial NF-e (pago)
                  ├── Webmania → emissão + monitor (pago)
                  └── DANFE Generator → conversão XML → PDF
```

---

## 2. Stack Tecnológica

| Componente | Tecnologia | Versão |
|---|---|---|
| **Servidor** | VPS Contabo Cloud | Ubuntu 24.04 LTS |
| **Runtime MCP** | Python 3.11+ | FastMCP |
| **Base MCP** | mcp-brasil (pip install) | Última |
| **Web Server** | Nginx | 1.24+ |
| **SSL** | Let's Encrypt (Certbot) | — |
| **Process Manager** | Systemd + Supervisor | — |
| **Container (opcional)** | Docker | 24+ |
| **NF-e Consulta** | Meu Danfe API (freemium) | REST |
| **NF-e Emissão (opcional)** | Webmania / NFE.io | REST |
| **Dados Governamentais** | Portal da Transparência API | Gratuito |

---

## 3. APIs e Fontes de Dados

### 3.1 APIs Gratuitas (já inclusas no mcp-brasil)

| API | Dados | Limite | Chave |
|---|---|---|---|
| **Portal da Transparência** | NFe Executivo Federal, contratos, licitações, servidores | 90 req/min | Token gratuito por email |
| **BrasilAPI** | CNPJ, CEP, DDD, bancos, feriados, FIPE | 10 req/min | Gratuita (aberta) |
| **BCB/SGS** | Selic, IPCA, câmbio, PIB, poupança | 60 req/min | Gratuita (aberta) |
| **IBGE** | Cidades, estados, população, PIB municipal, Censo | — | Gratuita (aberta) |
| **SICONFI** | RGF, RREO, dados contábeis municipais | — | Gratuita (aberta) |
| **Câmara dos Deputados** | Proposições, votações, deputados | 50 req/min | Gratuita (aberta) |
| **Senado Federal** | Matérias, votações, senadores | — | Gratuita (aberta) |

### 3.2 APIs Quase Grátis

| API | Custo | Dados | Limite |
|---|---|---|---|
| **Meu Danfe** | R$ 0,03/consulta (ou gratuito para DANFE) | Consulta NF-e por chave, geração DANFE PDF | Sem limite explícito |
| **infosimples** | Consultar preço | CNPJ completo, NFe PR | Consultar |

### 3.3 APIs Pagas (opcionais, para emissão)

| API | Custo | Dados |
|---|---|---|
| **Webmania** | R$ 199+/mês | Emissão NF-e/NFC-e/NFS-e/CT-e, monitor, validador IA |
| **NFE.io** | Consultar planos | Emissão + consulta NF-e, SDK Python |
| **Serpro Consulta NFe** | Pago por faixa | Consulta oficial RFB (OAuth2) |
| **LogAPI** | R$ 2.000+/mês | Rastreamento entregas (20+ transportadoras) |

---

## 4. Ferramentas MCP (Tools)

### 4.1 Ferramentas de NF-e

| Tool | Descrição | API Fonte |
|---|---|---|
| `consultar_nfe_por_chave(chave)` | Dados completos de NF-e por chave de acesso | Meu Danfe / Serpro |
| `gerar_danfe(chave)` | Gera PDF do DANFE para download | Meu Danfe |
| `consultar_nfe_por_cnpj(cnpj, periodo)` | Lista NF-e emitidas/recebidas por CNPJ | Portal Transparência / Webmania |
| `status_sefaz()` | Status atual dos serviços SEFAZ por estado | Webmania / SEFAZ direto |

### 4.2 Ferramentas de Produtos e Mercado

| Tool | Descrição | API Fonte |
|---|---|---|
| `consultar_produtos_por_ncm(ncm)` | Produtos vendidos por classificação NCM | Portal Transparência + IBGE |
| `analisar_tendencias_mercado(ncm, periodo)` | Tendências de preço e volume por NCM | Portal Transparência |
| `comparar_precos_produto(descricao)` | Comparação de preços entre regiões | Portal Transparência |
| `top_produtos_por_estado(uf, mes)` | Produtos mais vendidos por estado | Portal Transparência |

### 4.3 Ferramentas de CNPJ e Empresas

| Tool | Descrição | API Fonte |
|---|---|---|
| `consultar_cnpj(cnpj)` | Dados cadastrais completos da empresa | BrasilAPI |
| `consultar_socios(cnpj)` | Sócios e participações societárias | BrasilAPI |
| `consultar_empresas_por_atividade(cnae, uf)` | Empresas ativas por CNAE e localização | BrasilAPI / SICONFI |

### 4.4 Ferramentas Econômicas

| Tool | Descrição | API Fonte |
|---|---|---|
| `indicadores_economicos()` | IPCA, Selic, câmbio atual | BCB |
| `inflacao_acumulada(periodo)` | Inflação acumulada no período | BCB |
| `pib_por_municipio(ano)` | PIB dos municípios | IBGE |

---

## 5. Configuração do Servidor VPS

### 5.1 Especificações Mínimas

| Recurso | Mínimo | Recomendado |
|---|---|---|
| **Plano** | Cloud VPS S | Cloud VPS M |
| **CPU** | 2 vCores | 4 vCores |
| **RAM** | 4 GB | 8 GB |
| **Storage** | 50 GB SSD | 200 GB SSD |
| **SO** | Ubuntu 24.04 LTS | Ubuntu 24.04 LTS |
| **Custo** | ~6.99€/mês | ~13.99€/mês |

### 5.2 Software a Instalar

```bash
# Base
apt update && apt upgrade -y
apt install -y python3 python3-pip python3-venv nginx certbot git curl

# Python MCP
pip install mcp-brasil fastmcp uvicorn httpx

# Docker (opcional, para isolar serviços)
curl -fsSL https://get.docker.com | sh
```

### 5.3 Estrutura de Diretórios

```
/opt/mcp/
├── .env                     # Chaves de API
├── requirements.txt         # Dependências Python
├── server.py                # Servidor MCP principal
├── mcp_nfe/
│   ├── __init__.py
│   ├── tools_nfe.py         # Tools de NF-e
│   ├── tools_cnpj.py        # Tools de CNPJ
│   ├── tools_economia.py    # Tools econômicas
│   └── tools_mercado.py     # Tools de mercado
└── systemd/
    └── mcp-server.service   # Systemd unit
```

### 5.4 SSL com Let's Encrypt

```bash
certbot --nginx -d mcp.bytex.com.br
```

### 5.5 Systemd Service

```ini
[Unit]
Description=MCP Server Brasil
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/mcp
Environment=PYTHONUNBUFFERED=1
ExecStart=/usr/bin/python3 /opt/mcp/server.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

---

## 6. Implementação do Servidor MCP

### 6.1 `server.py` — Servidor Principal

```python
from fastmcp import FastMCP
from mcp_nfe.tools_nfe import register_nfe_tools
from mcp_nfe.tools_cnpj import register_cnpj_tools
from mcp_nfe.tools_economia import register_economia_tools
from mcp_nfe.tools_mercado import register_mercado_tools

mcp = FastMCP("mcp-brasil-nfe")

# Registrar todos os grupos de ferramentas
register_nfe_tools(mcp)
register_cnpj_tools(mcp)
register_economia_tools(mcp)
register_mercado_tools(mcp)

if __name__ == "__main__":
    # Modo SSE (HTTP) para integração com Bytex
    mcp.run(transport="sse", host="0.0.0.0", port=8000)
```

### 6.2 `tools_nfe.py` — Exemplo de Tool

```python
import httpx
import os

MEU_DANFE_TOKEN = os.getenv("MEU_DANFE_TOKEN")

def register_nfe_tools(mcp):
    
    @mcp.tool()
    async def consultar_nfe_por_chave(chave_acesso: str) -> dict:
        """
        Consulta dados completos de uma Nota Fiscal Eletrônica pela chave de acesso de 44 dígitos.
        Retorna dados do emitente, destinatário, produtos, impostos e transporte.
        """
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"https://api.meudanfe.com.br/api/nfe/{chave_acesso}",
                headers={"Authorization": f"Bearer {MEU_DANFE_TOKEN}"},
                timeout=15,
            )
        return resp.json()
    
    @mcp.tool()
    async def gerar_danfe(chave_acesso: str) -> str:
        """
        Gera o PDF do DANFE de uma NF-e e retorna a URL para download.
        """
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://api.meudanfe.com.br/api/danfe",
                json={"chave": chave_acesso},
                headers={"Authorization": f"Bearer {MEU_DANFE_TOKEN}"},
                timeout=30,
            )
        return resp.json().get("url", "")
```

---

## 7. Integração com Bytex AgentOS

### 7.1 Configuração do Agente

No Bytex AgentOS, o agente precisa ser configurado com o MCP client apontando para o servidor:

```python
# Configuração do agente
MCP_SERVERS = [
    {
        "name": "mcp-brasil-nfe",
        "url": "https://mcp.bytex.com.br/sse",
        "transport": "sse",
    }
]
```

### 7.2 Exemplos de Prompts para o Agente

| Pergunta do Usuário | Ação do Agente |
|---|---|
| "Quais produtos mais vendidos no Brasil em 2025?" | `top_produtos_por_estado()` + `consultar_produtos_por_ncm()` |
| "Analise a tendência de preços de notebooks" | `analisar_tendencias_mercado(ncm_notebook)` |
| "Verifique a NF-e 35200612345678901234567890123456789012345678" | `consultar_nfe_por_chave(chave)` |
| "Quanto custa o DANFE dessa nota?" | `gerar_danfe(chave)` |
| "Quais empresas em SP vendem móveis?" | `consultar_empresas_por_atividade(cnae_moveis, "SP")` |
| "Como está a inflação e a Selic?" | `indicadores_economicos()` |

---

## 8. Custo Mensal Estimado

| Item | Custo |
|---|---|
| **VPS Contabo** | €6.99 ~ €13.99/mês |
| **Meu Danfe** | ~R$ 3,00 a cada 100 consultas |
| **Webmania (opcional)** | R$ 199+/mês |
| **Domínio (opcional)** | ~R$ 40/ano |
| **Total mínimo** | **~€7/mês + R$ 3/mês** (apenas consulta) |
| **Total com emissão** | **~€14/mês + R$ 200/mês** |

---

## 9. Cronograma de Implementação

| Fase | O que | Tempo |
|---|---|---|
| **1** | Contratar VPS + configurar SO + Docker | 1 hora |
| **2** | Instalar mcp-brasil + configurar SSL | 2 horas |
| **3** | Desenvolver mcp-nfe (tools Meu Danfe + CNPJ) | 4 horas |
| **4** | Implementar tools de mercado e economia | 3 horas |
| **5** | Testar integração com Bytex AgentOS | 2 horas |
| **6** | Documentação + deploy final | 1 hora |
| | **Total** | **~13 horas** |

---

## 10. Próximos Passos

1. ☐ Contratar VPS Contabo
2. ☐ Obter chave da API Meu Danfe (cadastro gratuito)
3. ☐ Obter token do Portal da Transparência (cadastro por email)
4. ☐ Configurar domínio (ex: `mcp.bytex.com.br`) apontando para VPS
5. ☐ Fornecer credenciais SSH para configuração automatizada
6. ☐ Instalar e configurar servidor MCP
7. ☐ Testar tools no Bytex AgentOS

---

## 11. Referências

- [mcp-brasil (GitHub)](https://github.com/Mcp-Brasil/mcp-brasil)
- [Meu Danfe API](https://meudanfe.com.br/api)
- [Portal da Transparência API](https://portaldatransparencia.gov.br/api-de-dados)
- [Webmania NFe API](https://webmania.com.br/docs/rest-api-nfe/)
- [NFE.io](https://nfe.io/)
- [Serpro Consulta NFe](https://apicenter.estaleiro.serpro.gov.br/documentacao/consulta-nfe/)
- [FastMCP (Python)](https://github.com/jlowin/fastmcp)
- [Model Context Protocol](https://modelcontextprotocol.io)

---

*Documento gerado em 10/05/2026 — Bytex AgentOS*
