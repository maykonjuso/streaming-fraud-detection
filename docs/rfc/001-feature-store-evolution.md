# RFC-001: Evolution to a Feature Store / Evolução para Feature Store

> 🇺🇸 [English](#en) | 🇧🇷 [Português](#pt)

**Status:** Draft / Rascunho  
**Date / Data:** 2026-05-20  
**Author / Autor:** Maykon Junio Soares

---

<a id="en"></a>
## [EN] RFC-001: Evolution to a Feature Store

### Summary

This RFC proposes the introduction of a lightweight feature store to centralize feature computation, reuse features across models, and enable point-in-time correct feature retrieval for training — eliminating train/serve skew.

### Motivation

Currently, features are computed inline in `silver_job.py` (streaming) and in `ml/features/feature_engineering.py` (training). This creates two problems:

1. **Train/serve skew**: if the streaming feature logic drifts from the training logic, model performance degrades silently
2. **Feature duplication**: adding a new model requires duplicating feature computation

As the number of models grows (IsolationForest + ECOD + XGBoost today, potentially AutoARIMA for time-series patterns tomorrow), centralized feature management becomes critical.

### Proposed Solution

Introduce **Feast** (open source) as a lightweight feature store backed by Delta Lake (offline) and Redis (online):

```
Training pipeline
  └─ Feast offline store (Delta Lake Silver)
       └─ point-in-time correct feature retrieval

Streaming inference (Gold job)
  └─ Feast online store (Redis)
       └─ sub-millisecond feature lookup
```

Feature definitions live in `ml/features/feature_store.py` as Feast `FeatureView` objects. Both training and inference import from the same definitions.

### Open Questions

1. Is Redis overhead justified at current throughput (~1K msgs/sec)?
2. Should we use Feast or build a thin wrapper around Delta Lake + Redis directly?
3. Who owns feature definitions when a second team joins?

### Alternatives Considered

- **Tecton**: managed, but paid and overkill for this scope
- **Hopsworks**: open source but heavy operational overhead
- **Custom Delta Lake + Redis**: simpler but requires building point-in-time logic manually

### Rollout Plan

1. Phase 1: Define features in Feast, keep current pipeline unchanged (read-only validation)
2. Phase 2: Training pipeline reads from Feast offline store
3. Phase 3: Gold job reads from Feast online store (Redis)
4. Phase 4: Deprecate inline feature computation in `silver_job.py`

---

<a id="pt"></a>
## [PT] RFC-001: Evolução para Feature Store

### Sumário

Este RFC propõe a introdução de uma feature store leve para centralizar o cálculo de features, reutilizá-las entre modelos e habilitar recuperação de features point-in-time correta para treino — eliminando train/serve skew.

### Motivação

Atualmente, features são computadas inline em `silver_job.py` (streaming) e em `ml/features/feature_engineering.py` (treino). Isso cria dois problemas:

1. **Train/serve skew**: se a lógica de features no streaming divergir da lógica de treino, a performance do modelo degrada silenciosamente
2. **Duplicação de features**: adicionar um novo modelo requer duplicar o cálculo de features

Conforme o número de modelos cresce (IsolationForest + ECOD + XGBoost hoje, possivelmente AutoARIMA para padrões de séries temporais amanhã), gerenciamento centralizado de features se torna crítico.

### Solução Proposta

Introduzir **Feast** (open source) como feature store leve com backend em Delta Lake (offline) e Redis (online):

```
Pipeline de treino
  └─ Feast offline store (Delta Lake Silver)
       └─ recuperação de features point-in-time correta

Inferência em streaming (Gold job)
  └─ Feast online store (Redis)
       └─ lookup de features sub-milissegundo
```

Definições de features ficam em `ml/features/feature_store.py` como objetos Feast `FeatureView`. Tanto treino quanto inferência importam das mesmas definições.

### Perguntas em Aberto

1. O overhead do Redis é justificado no throughput atual (~1K msgs/seg)?
2. Devemos usar Feast ou construir um wrapper fino em cima de Delta Lake + Redis diretamente?
3. Quem é dono das definições de features quando um segundo time se juntar?

### Alternativas Consideradas

- **Tecton**: gerenciado, mas pago e excessivo para este escopo
- **Hopsworks**: open source mas overhead operacional pesado
- **Delta Lake + Redis custom**: mais simples, mas requer construir lógica point-in-time manualmente

### Plano de Rollout

1. Fase 1: Definir features no Feast, manter pipeline atual inalterado (validação somente-leitura)
2. Fase 2: Pipeline de treino lê do Feast offline store
3. Fase 3: Gold job lê do Feast online store (Redis)
4. Fase 4: Deprecar cálculo inline de features em `silver_job.py`
