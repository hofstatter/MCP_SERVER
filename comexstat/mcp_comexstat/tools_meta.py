import httpx
def register_meta_tools(mcp):
    @mcp.tool()
    async def ultima_atualizacao() -> str:
        '''Retorna a data da ultima atualizacao dos dados ComexStat.'''
        async with httpx.AsyncClient() as c:
            r = await c.get('https://api-comexstat.mdic.gov.br/general/dates/updated', timeout=10)
            data = r.json()
            return f"Ultima atualizacao: {data.get('data', {}).get('updated', 'desconhecida')}"

    @mcp.tool()
    async def anos_disponiveis() -> str:
        '''Retorna o intervalo de anos disponivel no ComexStat.'''
        async with httpx.AsyncClient() as c:
            r = await c.get('https://api-comexstat.mdic.gov.br/general/dates/years', timeout=10)
            data = r.json().get('data', {})
            return f"Dados disponiveis de {data.get('min')} a {data.get('max')}"
