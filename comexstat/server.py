from fastmcp import FastMCP
from mcp_comexstat.tools_consulta import register_consulta_tools
from mcp_comexstat.tools_meta import register_meta_tools
mcp = FastMCP('mcp-comexstat')
register_consulta_tools(mcp)
register_meta_tools(mcp)
if __name__ == '__main__':
    mcp.run(transport='sse', host='0.0.0.0', port=8001)
