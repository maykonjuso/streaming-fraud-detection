"""
MCP Server for fraud detection tools.
Servidor MCP para ferramentas de detecção de fraude.

EN: Exposes fraud API capabilities as MCP tools for use by the Claude API agent.
    Follows the same pattern deployed in production at Sicoob for N1 incident triage.
    See ADR-004 for architecture rationale.

PT: Expõe capacidades da API de fraude como ferramentas MCP para uso pelo agente Claude API.
    Segue o mesmo padrão implantado em produção no Sicoob para triagem de incidentes N1.
    Ver ADR-004 para justificativa de arquitetura.

Usage / Uso:
    python agents/mcp_server.py
"""

import logging

import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp_server")

API_BASE_URL = "http://localhost:8000"
server = Server("fraud-detection-mcp")


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="get_transaction",
            description=(
                "EN: Fetch details for a specific transaction. "
                "PT: Busca detalhes de uma transação específica."
            ),
            inputSchema={
                "type": "object",
                "properties": {"transaction_id": {"type": "string"}},
                "required": ["transaction_id"],
            },
        ),
        Tool(
            name="get_fraud_score",
            description=(
                "EN: Retrieve the ML ensemble fraud score for a transaction. "
                "PT: Recupera o score de fraude do ensemble ML para uma transação."
            ),
            inputSchema={
                "type": "object",
                "properties": {"transaction_id": {"type": "string"}},
                "required": ["transaction_id"],
            },
        ),
        Tool(
            name="list_recent_alerts",
            description=(
                "EN: List recent transactions flagged as potential fraud. "
                "PT: Lista transações recentes marcadas como potencial fraude."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "min_score": {"type": "number", "default": 0.7},
                    "limit": {"type": "integer", "default": 20},
                },
            },
        ),
        Tool(
            name="get_fraud_stats",
            description=(
                "EN: Get aggregate fraud statistics for a time window. "
                "PT: Obtém estatísticas agregadas de fraude para uma janela de tempo."
            ),
            inputSchema={
                "type": "object",
                "properties": {"window_hours": {"type": "integer", "default": 1}},
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    async with httpx.AsyncClient(base_url=API_BASE_URL, timeout=10.0) as client:
        if name == "get_transaction":
            resp = await client.get(f"/transactions/{arguments['transaction_id']}")
            return [TextContent(type="text", text=resp.text)]

        if name == "get_fraud_score":
            resp = await client.get(f"/scores/{arguments['transaction_id']}")
            return [TextContent(type="text", text=resp.text)]

        if name == "list_recent_alerts":
            resp = await client.get(
                "/scores/",
                params={
                    "min_score": arguments.get("min_score", 0.7),
                    "limit": arguments.get("limit", 20),
                },
            )
            return [TextContent(type="text", text=resp.text)]

        if name == "get_fraud_stats":
            resp = await client.post(
                "/graphql",
                json={
                    "query": f"""
                    query {{
                        fraudStats(windowHours: {arguments.get("window_hours", 1)}) {{
                            totalTransactions fraudCount fraudRate avgFraudScore maxFraudScore
                        }}
                    }}
                    """
                },
            )
            return [TextContent(type="text", text=resp.text)]

        return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def main():
    logger.info("Starting MCP server for fraud detection tools")
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
