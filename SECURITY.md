<div align="center">

# Security Policy / Política de Segurança

[English](#english) · [Português](#português)

</div>

---

## English

### Supported versions

| Version | Supported |
|---------|-----------|
| `main` branch | ✅ Yes |
| Tagged releases | ✅ Yes (latest only) |
| Older releases | ❌ No |

### Reporting a vulnerability

**Do not open a public GitHub issue for security vulnerabilities.**

Please report vulnerabilities by emailing **maykon.soaares@gmail.com** with:

- A description of the vulnerability and its potential impact.
- Steps to reproduce or proof of concept (if available).
- Any suggested mitigations.

You will receive an acknowledgement within **48 hours** and a resolution plan within **7 days**.

### Scope

This is a portfolio/educational project. The attack surface includes:

| Component | Notes |
|-----------|-------|
| FastAPI endpoints | Input validation via Pydantic; no auth layer in default setup |
| Kafka broker | No TLS in local Docker Compose — do **not** expose to public internet |
| MLflow | No auth in local setup — do **not** expose to public internet |
| Prometheus / Grafana | Default credentials (`admin/admin`) — change before any deployment |
| `.env` file | Contains `ANTHROPIC_API_KEY` — never commit this file |

### Security best practices for contributors

- Never commit secrets, API keys, or credentials.
- The `.gitignore` excludes `.env` — verify before every commit.
- Use `ANTHROPIC_API_KEY` only via environment variable or `.env` file (never hardcoded).
- Do not weaken or bypass Pydantic validation on API inputs.

---

## Português

### Versões suportadas

| Versão | Suportada |
|--------|-----------|
| Branch `main` | ✅ Sim |
| Releases com tag | ✅ Sim (apenas a mais recente) |
| Releases antigas | ❌ Não |

### Reportando uma vulnerabilidade

**Não abra uma issue pública no GitHub para vulnerabilidades de segurança.**

Reporte vulnerabilidades enviando um e-mail para **maykon.soaares@gmail.com** com:

- Descrição da vulnerabilidade e seu impacto potencial.
- Passos para reproduzir ou prova de conceito (se disponível).
- Sugestões de mitigação.

Você receberá uma confirmação em até **48 horas** e um plano de resolução em até **7 dias**.

### Escopo

Este é um projeto de portfólio/educacional. A superfície de ataque inclui:

| Componente | Observações |
|------------|-------------|
| Endpoints FastAPI | Validação de entrada via Pydantic; sem camada de autenticação na configuração padrão |
| Broker Kafka | Sem TLS no Docker Compose local — **não** expor à internet pública |
| MLflow | Sem autenticação na configuração local — **não** expor à internet pública |
| Prometheus / Grafana | Credenciais padrão (`admin/admin`) — alterar antes de qualquer deploy |
| Arquivo `.env` | Contém `ANTHROPIC_API_KEY` — nunca commitar este arquivo |

### Boas práticas de segurança para contribuidores

- Nunca commitar segredos, chaves de API ou credenciais.
- O `.gitignore` exclui `.env` — verifique antes de cada commit.
- Use `ANTHROPIC_API_KEY` apenas via variável de ambiente ou arquivo `.env` (nunca hardcoded).
- Não enfraqueça ou contorne a validação Pydantic nas entradas da API.
