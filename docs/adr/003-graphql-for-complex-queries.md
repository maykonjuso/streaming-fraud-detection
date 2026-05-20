# ADR-003: GraphQL for Complex Fraud Queries / GraphQL para Queries Complexas de Fraude

> 🇺🇸 [English](#en) | 🇧🇷 [Português](#pt)

---

<a id="en"></a>
## [EN] ADR-003: GraphQL for Complex Fraud Queries

**Status:** Accepted  
**Date:** 2026-05-20  
**Author:** Maykon Junio Soares

### Context

The API needs to serve multiple consumers with different data needs:

- **Dashboards**: need aggregated metrics (fraud rate by region, time-series of scores)
- **Analysts**: need ad-hoc filtering (transactions above threshold X, in window Y, from account Z)
- **Agents (LLM)**: need flexible queries to answer natural language questions

Exposing a new REST endpoint per query combination would create endpoint proliferation and increase maintenance burden.

### Decision

Expose a **GraphQL endpoint** (via Strawberry) alongside REST endpoints.

- REST: operational endpoints (`/health`, `/scores/{id}`, `/metrics`)
- GraphQL: complex, multi-dimensional queries over transaction and fraud data
- WebSocket: real-time fraud alert push

### Rationale

GraphQL allows consumers to request exactly the fields they need, reducing over-fetching. It is particularly valuable for the LLM agent, which needs to compose arbitrary queries based on natural language input without requiring new API versions.

Strawberry was chosen over Ariadne because it is Python-first (type annotations), integrates cleanly with FastAPI, and requires no separate SDL files.

### Consequences

**Positive:**
- Single endpoint handles all complex query patterns
- LLM agent can compose queries dynamically
- No endpoint proliferation as new filtering needs arise

**Negative:**
- GraphQL adds learning curve for contributors unfamiliar with it
- N+1 query problem requires DataLoader implementation for production load
- Introspection should be disabled in production to limit attack surface

---

<a id="pt"></a>
## [PT] ADR-003: GraphQL para Queries Complexas de Fraude

**Status:** Aceito  
**Data:** 2026-05-20  
**Autor:** Maykon Junio Soares

### Contexto

A API precisa servir múltiplos consumidores com necessidades de dados diferentes:

- **Dashboards**: precisam de métricas agregadas (taxa de fraude por região, série temporal de scores)
- **Analistas**: precisam de filtros ad-hoc (transações acima do threshold X, na janela Y, da conta Z)
- **Agentes (LLM)**: precisam de queries flexíveis para responder perguntas em linguagem natural

Expor um novo endpoint REST por combinação de query criaria proliferação de endpoints e aumentaria o custo de manutenção.

### Decisão

Expor um **endpoint GraphQL** (via Strawberry) junto dos endpoints REST.

- REST: endpoints operacionais (`/health`, `/scores/{id}`, `/metrics`)
- GraphQL: queries complexas e multidimensionais sobre dados de transação e fraude
- WebSocket: push de alertas de fraude em tempo real

### Justificativa

GraphQL permite que consumidores solicitem exatamente os campos que precisam, reduzindo over-fetching. É especialmente valioso para o agente LLM, que precisa compor queries arbitrárias baseadas em input em linguagem natural sem requerer novas versões de API.

Strawberry foi escolhido em vez de Ariadne por ser Python-first (anotações de tipo), integrar limpamente com FastAPI e não requerer arquivos SDL separados.

### Consequências

**Positivas:**
- Endpoint único lida com todos os padrões de query complexa
- Agente LLM pode compor queries dinamicamente
- Sem proliferação de endpoints conforme novas necessidades de filtro surgem

**Negativas:**
- GraphQL adiciona curva de aprendizado para contribuidores não familiarizados
- Problema N+1 requer implementação de DataLoader para carga em produção
- Introspection deve ser desabilitada em produção para limitar superfície de ataque
