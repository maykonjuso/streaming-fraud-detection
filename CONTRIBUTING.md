<div align="center">

# Contributing / Contribuindo

[English](#english) · [Português](#português)

</div>

---

## English

### Getting started

1. **Fork** the repository and clone your fork.
2. Create a branch from `main`:
   ```bash
   git checkout -b feat/my-feature
   ```
3. Install dependencies:
   ```bash
   make install
   ```
4. Install pre-commit hooks:
   ```bash
   pip install pre-commit
   pre-commit install
   ```

### Development workflow

```bash
make lint          # ruff check + format check (--no-cache)
make test          # unit tests with coverage (≥ 80%)
make health-check  # verify all services respond
```

All checks must pass before opening a PR. The CI pipeline enforces the same gates.

### Branch naming

| Prefix | Use |
|--------|-----|
| `feat/` | New feature |
| `fix/` | Bug fix |
| `docs/` | Documentation only |
| `refactor/` | Code change without fix or feature |
| `chore/` | Build, tooling, CI |
| `perf/` | Performance improvement |

### Commit messages

This project follows [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>[optional scope]: <description>

[optional body]

[optional footer]
```

Examples:
```
feat(api): add p99 latency endpoint
fix(gold_job): handle empty DataFrame from Silver
docs(adr): add ADR-005 for feature store migration
```

### Pull requests

- Fill in the PR template completely.
- Link the related issue with `Closes #<number>`.
- Keep PRs focused — one concern per PR.
- All tests must pass and coverage must not drop below 80%.
- At least one review approval is required before merge.

### Documentation

- All documentation must be **bilingual** (English + Portuguese) in the same file.
- Use `[English](#english) · [Português](#português)` anchor nav at the top.
- ADRs go in `docs/adr/`, RFCs in `docs/rfc/`, runbooks in `docs/runbooks/`.

### Code style

- Formatter and linter: [ruff](https://docs.astral.sh/ruff/) (configured in `pyproject.toml`).
- Line length: 100 characters.
- Target: Python 3.11+.
- No inline comments unless the **why** is non-obvious.

---

## Português

### Primeiros passos

1. **Fork** o repositório e clone seu fork.
2. Crie uma branch a partir de `main`:
   ```bash
   git checkout -b feat/minha-funcionalidade
   ```
3. Instale as dependências:
   ```bash
   make install
   ```
4. Instale os hooks de pre-commit:
   ```bash
   pip install pre-commit
   pre-commit install
   ```

### Fluxo de desenvolvimento

```bash
make lint          # ruff check + verificação de formatação (--no-cache)
make test          # testes unitários com cobertura (≥ 80%)
make health-check  # verificar se todos os serviços respondem
```

Todas as verificações devem passar antes de abrir um PR. O pipeline de CI aplica as mesmas regras.

### Nomenclatura de branches

| Prefixo | Uso |
|---------|-----|
| `feat/` | Nova funcionalidade |
| `fix/` | Correção de bug |
| `docs/` | Somente documentação |
| `refactor/` | Mudança de código sem correção ou feature |
| `chore/` | Build, ferramentas, CI |
| `perf/` | Melhoria de performance |

### Mensagens de commit

Este projeto segue [Conventional Commits](https://www.conventionalcommits.org/):

```
<tipo>[escopo opcional]: <descrição>

[corpo opcional]

[rodapé opcional]
```

Exemplos:
```
feat(api): adicionar endpoint de latência p99
fix(gold_job): tratar DataFrame vazio do Silver
docs(adr): adicionar ADR-005 para migração do feature store
```

### Pull requests

- Preencha o template de PR completamente.
- Vincule a issue relacionada com `Closes #<número>`.
- Mantenha PRs focados — uma preocupação por PR.
- Todos os testes devem passar e a cobertura não deve cair abaixo de 80%.
- Pelo menos uma aprovação de review é necessária antes do merge.

### Documentação

- Toda documentação deve ser **bilíngue** (inglês + português) no mesmo arquivo.
- Use navegação por âncoras `[English](#english) · [Português](#português)` no topo.
- ADRs vão em `docs/adr/`, RFCs em `docs/rfc/`, runbooks em `docs/runbooks/`.

### Estilo de código

- Formatador e linter: [ruff](https://docs.astral.sh/ruff/) (configurado em `pyproject.toml`).
- Comprimento de linha: 100 caracteres.
- Alvo: Python 3.11+.
- Sem comentários inline a menos que o **porquê** não seja óbvio.
