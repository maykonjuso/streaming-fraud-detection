"""
Claude API fraud triage agent.
Agente de triagem de fraude Claude API.

EN: Uses the Anthropic Claude API with MCP tool access to automatically classify
    incoming fraud alerts by severity, enrich them with context from the API,
    and generate structured triage summaries for analysts.

PT: Usa a API Claude da Anthropic com acesso a ferramentas MCP para classificar
    automaticamente alertas de fraude por severidade, enriquecê-los com contexto
    da API e gerar sumários estruturados de triagem para analistas.

Usage / Uso:
    python agents/fraud_agent.py --transaction-id <id>
    python agents/fraud_agent.py --mode watch  # watches for new high-score alerts
"""

import argparse
import asyncio
import json
import logging
import os

import anthropic

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("fraud_agent")

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
MODEL = "claude-sonnet-4-6"

SYSTEM_PROMPT = """You are a fraud analyst assistant for a financial transaction monitoring system.

You have access to tools that query the fraud detection API:
- get_transaction: fetch raw transaction details
- get_fraud_score: retrieve ML ensemble scores (IsolationForest + ECOD + XGBoost)
- list_recent_alerts: list recent high-score transactions
- get_fraud_stats: aggregate statistics for a time window

When triaging a fraud alert:
1. Retrieve the transaction details and fraud score
2. Check if the account has other recent high-score transactions (velocity pattern)
3. Classify severity: HIGH (score >= 0.8), MEDIUM (0.5-0.8), LOW (< 0.5)
4. Identify the fraud type: account_takeover, card_not_present, unusual_geography, velocity_abuse, other
5. Return a structured JSON triage report

Always respond in the language of the user's request (Portuguese or English).
"""


def get_mcp_tools() -> list[dict]:
    """
    EN: Returns tool definitions matching the MCP server's exposed tools.
    PT: Retorna definições de ferramentas correspondentes às ferramentas expostas pelo servidor MCP.
    """
    return [
        {
            "name": "get_fraud_score",
            "description": "Retrieve the ML ensemble fraud score for a transaction.",
            "input_schema": {
                "type": "object",
                "properties": {"transaction_id": {"type": "string"}},
                "required": ["transaction_id"],
            },
        },
        {
            "name": "list_recent_alerts",
            "description": "List recent transactions flagged as potential fraud.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "min_score": {"type": "number"},
                    "limit": {"type": "integer"},
                },
            },
        },
        {
            "name": "get_fraud_stats",
            "description": "Get aggregate fraud statistics for a time window.",
            "input_schema": {
                "type": "object",
                "properties": {"window_hours": {"type": "integer"}},
            },
        },
    ]


async def triage_alert(transaction_id: str) -> dict:
    """
    EN: Run the Claude agent to triage a specific fraud alert.
    PT: Executa o agente Claude para triar um alerta de fraude específico.
    """
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    messages = [
        {
            "role": "user",
            "content": (
                f"Triage the fraud alert for transaction {transaction_id}. "
                "Retrieve its score and check for velocity patterns on the same account "
                "in the last hour. Return a JSON triage report with: "
                "severity, fraud_type, recommended_action, summary."
            ),
        }
    ]

    tools = get_mcp_tools()

    while True:
        response = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            tools=tools,
            messages=messages,
        )

        if response.stop_reason == "end_turn":
            for block in response.content:
                if hasattr(block, "text"):
                    try:
                        return json.loads(block.text)
                    except json.JSONDecodeError:
                        return {"summary": block.text}
            break

        if response.stop_reason == "tool_use":
            tool_calls = [b for b in response.content if b.type == "tool_use"]
            messages.append({"role": "assistant", "content": response.content})

            tool_results_content = []
            for tool_call in tool_calls:
                result = await _execute_tool(tool_call.name, tool_call.input)
                tool_results_content.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": tool_call.id,
                        "content": json.dumps(result),
                    }
                )

            messages.append({"role": "user", "content": tool_results_content})

    return {"error": "Agent did not produce a triage report"}


async def _execute_tool(tool_name: str, tool_input: dict) -> dict:
    """
    EN: Execute a tool call against the fraud detection API.
    PT: Executa uma chamada de ferramenta contra a API de detecção de fraude.
    """
    import httpx

    async with httpx.AsyncClient(base_url="http://localhost:8000", timeout=10.0) as client:
        if tool_name == "get_fraud_score":
            resp = await client.get(f"/scores/{tool_input['transaction_id']}")
            return resp.json()
        if tool_name == "list_recent_alerts":
            resp = await client.get("/scores/", params=tool_input)
            return resp.json()
        if tool_name == "get_fraud_stats":
            return {"error": "not implemented"}
        return {"error": f"unknown tool {tool_name}"}


def main():
    parser = argparse.ArgumentParser(description="Fraud alert triage agent")
    parser.add_argument("--transaction-id", required=True, help="Transaction ID to triage")
    args = parser.parse_args()

    report = asyncio.run(triage_alert(args.transaction_id))
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
