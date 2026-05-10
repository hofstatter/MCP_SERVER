import httpx
BASE = 'https://api-comexstat.mdic.gov.br'

async def _query(flow, ano, mes=None, pais=None, estado=None, ncm=None):
    period = {'from': f'{ano}-01', 'to': f'{ano}-12'}
    filters = []
    details = ['ncm']
    if mes:
        period = {'from': f'{ano}-{mes:02d}', 'to': f'{ano}-{mes:02d}'}
    if pais:
        filters.append({'filter': 'country', 'values': [pais]})
        details.append('country')
    if estado:
        filters.append({'filter': 'state', 'values': [estado]})
        details.append('state')
    if ncm:
        filters.append({'filter': 'ncm', 'values': [ncm]})
    payload = {'flow': flow, 'monthDetail': bool(mes), 'period': period, 'metrics': ['metricFOB', 'metricKG']}
    if filters: payload['filters'] = filters
    if details: payload['details'] = details
    async with httpx.AsyncClient(timeout=30) as c:
        r = await c.post(f'{BASE}/general', json=payload)
        return r.json()

def register_consulta_tools(mcp):
    @mcp.tool()
    async def consultar_exportacao(ano: int, mes: int = None, pais: int = None, estado: int = None, ncm: str = None) -> dict:
        '''Consulta dados de exportacao do Brasil por ano, mes, pais, estado ou NCM.'''
        return await _query('export', ano, mes, pais, estado, ncm)

    @mcp.tool()
    async def consultar_importacao(ano: int, mes: int = None, pais: int = None, estado: int = None, ncm: str = None) -> dict:
        '''Consulta dados de importacao do Brasil por ano, mes, pais, estado ou NCM.'''
        return await _query('import', ano, mes, pais, estado, ncm)
