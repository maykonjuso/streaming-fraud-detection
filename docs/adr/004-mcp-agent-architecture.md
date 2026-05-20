# ADR-004: MCP Agent for Alert Triage / Agente MCP para Triagem de Alertas

> 🇺🇸 [English](#en) | 🇧🇷 [Português](#pt)

---

<a id="en"></a>
## [EN] ADR-004: MCP Agent for Alert Triage

**Status:** Accepted  
**Date:** 2026-05-20  
**Author:** Maykon Junio Soares

### Context

High-throughput fraud detection generates a large number of alerts that require classification and prioritization. Without intelligent triage, analysts face alert fatigue and high-severity fraud events can be buried in noise.

We need an automated layer that:
- Classifies incoming fraud alerts by severity and type
- Enriches alerts with contextual information from the API
- Provides natural language summaries for human review
- Can be queried conversationally for fraud pattern analysis

### Decision

Build an **MCP (Model Context Protocol) server** that exposes fraud API tools to a **Claude API agent**, following the same architecture pattern deployed in production at Sicoob for N1 incident triage.

The MCP server exposes tools:
- `get_transaction(id)`: fetch transaction details from Delta Gold
- `get_fraud_score(id)`: retrieve ML scores for a transaction
- `list_recent_alerts(limit, min_score)`: list recent high-score transactions
- `get_fraud_stats(window_hours)`: aggregate fraud statistics for a time window
- `query_transactions(filters)`: flexible transaction search

The Claude API agent uses these tools to classify alerts, enrich them with context, and produce structured summaries.

### Rationale

MCP provides a standardized protocol for exposing API capabilities to LLMs, avoiding the need to build custom tool-calling logic. This pattern was validated in production (Sicoob N1 agent + audit agent), demonstrating that Claude can reliably use structured tools to triage domain-specific incidents.

### Consequences

**Positive:**
- Reuses battle-tested pattern from production (Sicoob)
- MCP server is independently testable and reusable
- Natural language interface reduces analyst cognitive load
- Claude handles context aggregation across multiple tool calls

**Negative:**
- Requires Anthropic API key (cost per token)
- Adds latency to the triage path (~1-3 seconds per alert)
- MCP server must stay in sync with API schema changes

---

<a id="pt"></a>
## [PT] ADR-004: Agente MCP para Triagem de Alertas

**Status:** Aceito  
**Data:** 2026-05-20  
**Autor:** Maykon Junio Soares

### Contexto

Detecção de fraude em alto volume gera um grande número de alertas que precisam de classificação e priorização. Sem triagem inteligente, analistas enfrentam fadiga de alertas e eventos de fraude de alta severidade podem ser enterrados no ruído.

Precisamos de uma camada automatizada que:
- Classifique alertas de fraude por severidade e tipo
- Enriqueça alertas com informações contextuais da API
- Forneça sumários em linguagem natural para revisão humana
- Possa ser consultada conversacionalmente para análise de padrões de fraude

### Decisão

Construir um **servidor MCP (Model Context Protocol)** que expõe ferramentas da API de fraude para um **agente Claude API**, seguindo o mesmo padrão de arquitetura implantado em produção no Sicoob para triagem de incidentes N1.

O servidor MCP expõe ferramentas:
- `get_transaction(id)`: busca detalhes da transação no Delta Gold
- `get_fraud_score(id)`: recupera scores ML para uma transação
- `list_recent_alerts(limit, min_score)`: lista transações recentes com score alto
- `get_fraud_stats(window_hours)`: estatísticas agregadas de fraude para uma janela de tempo
- `query_transactions(filters)`: busca flexível de transações

O agente Claude API usa essas ferramentas para classificar alertas, enriquecê-los com contexto e produzir sumários estruturados.

### Justificativa

MCP fornece um protocolo padronizado para expor capacidades de API a LLMs, evitando a necessidade de construir lógica custom de tool-calling. Esse padrão foi validado em produção (agente N1 Sicoob + agente de auditoria), demonstrando que Claude consegue usar ferramentas estruturadas de forma confiável para triar incidentes de domínio específico.

### Consequências

**Positivas:**
- Reutiliza padrão testado em produção (Sicoob)
- Servidor MCP é independentemente testável e reutilizável
- Interface em linguagem natural reduz carga cognitiva do analista
- Claude lida com agregação de contexto entre múltiplas chamadas de ferramentas

**Negativas:**
- Requer chave de API da Anthropic (custo por token)
- Adiciona latência ao caminho de triagem (~1-3 segundos por alerta)
- Servidor MCP deve permanecer sincronizado com mudanças de schema da API
