# ADR-001: Delta Lake over Pure Parquet / Delta Lake em vez de Parquet puro

> 🇺🇸 [English](#en) | 🇧🇷 [Português](#pt)

---

<a id="en"></a>
## [EN] ADR-001: Delta Lake over Pure Parquet

**Status:** Accepted  
**Date:** 2026-05-20  
**Author:** Maykon Junio Soares

### Context

The streaming pipeline continuously writes micro-batches of data. We need a storage format that supports:

- Concurrent writes from multiple Spark jobs without corruption
- Ability to reprocess historical events
- Schema evolution without downtime
- Efficient timestamp-based reads for the serving layer

Alternatives considered: pure Parquet, Apache Iceberg, and Delta Lake (delta-spark, open source).

### Decision

Use **Delta Lake via delta-spark** (open source, no Databricks dependency).

### Rationale

| Criterion | Pure Parquet | Iceberg | Delta Lake |
|-----------|-------------|---------|-----------|
| ACID in streaming | No | Yes | Yes |
| Time travel | No | Yes | Yes |
| Schema evolution | Manual | Yes | Yes |
| PySpark integration | Native | Requires config | Simple via `delta-spark` |
| Auto-compaction | No | Yes | Yes (`OPTIMIZE`) |

Delta Lake was chosen for its **simpler PySpark integration** (`DeltaTable.forPath`) and alignment with the Databricks production setup at Sicoob, reducing the learning curve when scaling this project.

The **Bronze/Silver/Gold (medallion)** pattern separates responsibilities clearly:
- **Bronze**: raw Kafka events, no transformation, only ingestion metadata
- **Silver**: cleaned data with calculated features
- **Gold**: ML scores, ready for serving

### Consequences

**Positive:**
- Simple reprocessing via `RESTORE TABLE`
- Schema evolution without rewriting partitions
- `OPTIMIZE` + `ZORDER` reduces read latency for API queries

**Negative:**
- Adds `delta-spark` dependency (~50 MB)
- Requires Spark 3.3+ for full Deletion Vectors support
- `_delta_log/` adds metadata overhead on small volumes

### Rejected Alternatives

- **Pure Parquet**: no ACID, no time travel, impossible to guarantee consistency in parallel streaming
- **Apache Iceberg**: superior in some aspects, but PySpark integration requires additional catalog configuration; Delta Lake is sufficient for the current scope

---

<a id="pt"></a>
## [PT] ADR-001: Delta Lake em vez de Parquet puro

**Status:** Aceito  
**Data:** 2026-05-20  
**Autor:** Maykon Junio Soares

### Contexto

O pipeline de streaming grava continuamente micro-batches de dados. Precisamos de um formato de armazenamento que suporte:

- Escritas concorrentes de múltiplos jobs Spark sem corrupção
- Capacidade de re-processar eventos históricos
- Schema evolution sem downtime
- Leitura eficiente por timestamp para a camada de serving

Alternativas consideradas: Parquet puro, Apache Iceberg e Delta Lake (delta-spark, open source).

### Decisão

Usar **Delta Lake via delta-spark** (open source, sem dependência de Databricks).

### Justificativa

| Critério | Parquet puro | Iceberg | Delta Lake |
|----------|-------------|---------|-----------|
| ACID em streaming | Não | Sim | Sim |
| Time travel | Não | Sim | Sim |
| Schema evolution | Manual | Sim | Sim |
| Integração PySpark | Nativa | Requer config | Simples via `delta-spark` |
| Compaction automático | Não | Sim | Sim (`OPTIMIZE`) |

Delta Lake foi escolhido pela **integração mais simples com PySpark** (`DeltaTable.forPath`) e por alinhar com o setup Databricks em produção no Sicoob, reduzindo a curva de aprendizado ao escalar este projeto.

O padrão **Bronze/Silver/Gold (medallion)** separa claramente responsabilidades:
- **Bronze**: eventos brutos do Kafka, sem transformação, apenas metadados de ingestão
- **Silver**: dados limpos com features calculadas
- **Gold**: scores de ML, pronto para serving

### Consequências

**Positivas:**
- Reprocessamento simples via `RESTORE TABLE`
- Schema evolution sem reescrever partições
- `OPTIMIZE` + `ZORDER` reduz latência de leitura nas queries da API

**Negativas:**
- Adiciona dependência `delta-spark` (~50 MB)
- Requer Spark 3.3+ para suporte completo a Deletion Vectors
- `_delta_log/` adiciona overhead de metadados em volumes pequenos

### Alternativas rejeitadas

- **Parquet puro**: sem ACID, sem time travel, impossível garantir consistência em streaming paralelo
- **Apache Iceberg**: superior em alguns aspectos, mas integração PySpark requer configuração adicional de catalog; Delta Lake é suficiente para o escopo atual
