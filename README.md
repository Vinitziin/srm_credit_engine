# SRM Credit Engine

Plataforma de cessão de crédito multimoedas: recebe recebíveis, precifica com deságio por tipo de ativo e liquida transações de forma ACID. Entrega do [desafio técnico da SRM Asset](CASE.md).

- **Backend:** FastAPI + SQLAlchemy 2.0 async + asyncpg + Alembic + PostgreSQL 16
- **Frontend:** React 18 + TypeScript + Vite + Tailwind + TanStack Query/Table + React Router
- **Infra:** Docker Compose · CI no GitHub Actions · pre-commit com ruff e tsc

---

## TL;DR — Rodando

Pré-requisitos: Docker + Docker Compose.

```bash
docker-compose up --build
```

Ao subir, o backend roda `alembic upgrade head` automaticamente (migrations + seed de moedas e tipos de recebíveis).

- Frontend: http://localhost:5173
- API: http://localhost:8000
- Swagger: http://localhost:8000/docs
- Healthcheck: http://localhost:8000/health

Smoke test manual:

1. Cadastrar um cedente em `/cedentes`
2. Simular um recebível em `/` (VP atualiza em tempo real com debounce de 400ms)
3. Clicar em **Liquidar** → redireciona pra `/statements`
4. Reverter a transação pelo botão na listagem

---

## Endpoints principais

Todos sob o prefixo `/api/v1`. Detalhes e schemas no Swagger.

| Método | Path                                   | Propósito                                                    |
|--------|----------------------------------------|--------------------------------------------------------------|
| GET    | `/currencies`                          | Lista moedas cadastradas                                     |
| GET    | `/receivable-types`                    | Lista tipos de recebível (com spread)                        |
| GET    | `/exchange-rates`                      | Busca taxa de câmbio atual entre duas moedas                 |
| POST   | `/exchange-rates`                      | Registra taxa manual                                         |
| POST   | `/exchange-rates/refresh`              | Atualiza taxa via provedor externo mockado (com retry)       |
| GET    | `/cedentes`                            | Lista cedentes                                               |
| POST   | `/cedentes`                            | Cadastra cedente                                             |
| POST   | `/simulate`                            | Calcula valor presente sem persistir (cross-currency supported) |
| POST   | `/transactions`                        | Liquida um recebível (ACID)                                  |
| GET    | `/transactions/{id}`                   | Busca transação                                              |
| PATCH  | `/transactions/{id}/status`            | Atualiza status com optimistic locking (exige `version`)     |
| GET    | `/reports/statements`                  | Extrato de liquidação com filtros e paginação server-side    |

---

## Estrutura do monorepo

```
srm-credit-engine/
├── backend/
│   ├── app/
│   │   ├── api/v1/            # rotas
│   │   ├── services/          # pricing strategies, exchange client
│   │   ├── repositories/      # acesso a dados (ORM + SQL nativo em reports)
│   │   ├── schemas/           # DTOs Pydantic
│   │   ├── models/            # SQLAlchemy models
│   │   ├── exceptions.py      # handlers globais
│   │   └── logging.py         # structlog + RequestId + AccessLog middlewares
│   ├── alembic/               # migrations + seed
│   ├── tests/                 # pytest (unit + integration contra Postgres real)
│   └── pyproject.toml
├── frontend/
│   └── src/
│       ├── api/               # axios + wrappers por recurso
│       ├── hooks/             # React Query hooks
│       ├── components/        # UI reutilizável
│       ├── pages/             # Simulator, Statements, Cedentes
│       └── types/api.ts       # DTOs espelhando o backend
├── docs/
│   ├── C4.md                  # diagramas Context + Container
│   ├── ER.md                  # diagrama ER
│   └── ddl.sql                # schema dump
├── docker-compose.yml
├── .github/workflows/ci.yml
├── .pre-commit-config.yaml
├── ARQUITETURA.md             # decisões de design (referência viva)
├── AI_USAGE.md                # uso de IA na construção do projeto
└── CASE.md                    # enunciado original do desafio
```

Para visão de design mais profunda (por que cada decisão foi tomada), ver [ARQUITETURA.md](ARQUITETURA.md).

---

## Testes

33 testes cobrindo strategies de pricing, câmbio, transações ACID, optimistic locking e relatórios.

```bash
docker-compose exec backend pytest -v
```

Integration tests rodam contra o Postgres real do compose — cada teste isola os dados via `TRUNCATE ... CASCADE` + `engine.dispose()` para evitar reuso de conexões entre event loops.

---

## Observabilidade

Logs JSON via `structlog`. Middlewares registrados em [backend/app/logging.py](backend/app/logging.py):

- `RequestIdMiddleware` — injeta `request_id` no contexto de todo log da request (aceita `X-Request-ID` do cliente ou gera um UUID).
- `AccessLogMiddleware` — emite `http_request` com `method`, `path`, `status_code`, `duration_ms`. Ignora `/health` pra não poluir probes.

Eventos de negócio estruturados:

- `transaction.created` — id, cedente, face, PV, moedas, flag cross-currency
- `transaction.status_changed` — id, from, to, nova version
- `simulation.computed` (DEBUG) — face, spread, PV, flag cross-currency

Amostra de log:

```json
{"event":"http_request","method":"POST","path":"/api/v1/transactions","status_code":201,"duration_ms":38.47,"request_id":"c5b7...","level":"info","timestamp":"2026-04-17T..."}
{"event":"transaction.created","transaction_id":"5e2b...","face_value":"10000","present_value":"9815.12","currency":"BRL","payment_currency":"USD","cross_currency":true,"request_id":"c5b7...","level":"info","timestamp":"..."}
```

---

## Fluxo de trabalho Git

GitHub Flow: `main` sempre estável, toda mudança em branch `feature/*` ou `docs/*`, merge via `--no-ff` para preservar o histórico da feature.

Commits seguem [Conventional Commits](https://www.conventionalcommits.org/). As 9 fases do projeto foram entregues em branches separadas:

| # | Fase                            | Branch                     |
|---|---------------------------------|----------------------------|
| 1 | Infra + FastAPI base            | `feature/infra-setup`      |
| 2 | Models + Alembic + DDL          | `feature/data-models`      |
| 3 | Currency engine (retry)         | `feature/currency-engine`  |
| 4 | Pricing (Strategy + testes)     | `feature/pricing-strategy` |
| 5 | Transactions (ACID + lock)      | `feature/transactions`     |
| 6 | Reports (SQL nativo)            | `feature/reports`          |
| 7 | Frontend completo               | `feature/frontend`         |
| 8 | Logs + CI + pre-commit          | `feature/observability-ci` |
| 9 | Docs (C4, ER, AI_USAGE)         | `docs/architecture`        |

A entrega final está marcada com a tag `v1.0.0`.

---

## CI

[`.github/workflows/ci.yml`](.github/workflows/ci.yml) roda em `push` para `main` e em todo PR:

- **backend** — Python 3.12, `ruff check` + `ruff format --check`, `alembic upgrade head` contra um `postgres:16-alpine` ephemeral como service, `pytest -q`.
- **frontend** — Node 20, `npm install`, `npx tsc -b`.

---

## Pre-commit (opcional, recomendado)

Config em [`.pre-commit-config.yaml`](.pre-commit-config.yaml): hooks de whitespace/EOF/YAML + `ruff` (backend) + `tsc` (frontend via node local).

```bash
pip install pre-commit
pre-commit install
```

---

## Documentação adicional

- [ARQUITETURA.md](ARQUITETURA.md) — decisões de design e filosofia do projeto
- [docs/C4.md](docs/C4.md) — diagramas C4 (Context + Container)
- [docs/ER.md](docs/ER.md) — diagrama entidade-relacionamento
- [docs/ddl.sql](docs/ddl.sql) — schema SQL
- [AI_USAGE.md](AI_USAGE.md) — uso de IA ao longo do projeto
- [CASE.md](CASE.md) — enunciado do desafio
