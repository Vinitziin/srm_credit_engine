# SRM Credit Engine — Arquitetura

> Referência para agentes de desenvolvimento. Escopo funcional completo em `CASE.md`.
>
> **Filosofia:** entregar o obrigatório funcionando bem. Simples, testado, explicável.
> Tudo que não está aqui é melhoria futura — e está sinalizado como tal.

---

## 1. Stack

| Camada     | Tecnologia                       | Por quê                                                  |
|------------|----------------------------------|----------------------------------------------------------|
| Backend    | Python 3.12 + FastAPI            | Tipagem via Pydantic, Swagger automático, async           |
| ORM        | SQLAlchemy 2.0                   | ORM onde faz sentido, `text()` nos relatórios             |
| Migrations | Alembic                          | Autogenerate a partir dos models                          |
| Banco      | PostgreSQL 16                    | ACID, `NUMERIC` pra valores financeiros                   |
| Frontend   | React 18 + TypeScript + Vite     | Ecossistema amplo, tipagem, build rápido                  |
| Estilo     | Tailwind CSS                     | Rápido e consistente                                      |
| Data Grid  | TanStack Table                   | Paginação server-side headless                            |
| Server State | TanStack Query                 | Cache, loading/error states                               |
| Testes     | pytest (back) · Vitest (front)   | Cobertura das strategies                                  |
| Infra      | Docker Compose                   | Um comando sobe tudo                                      |
| Logs       | structlog                        | JSON estruturado, request_id                              |
| CI         | GitHub Actions                   | Lint + testes no push                                     |

---

## 2. Estrutura do Monorepo

```
srm-credit-engine/
├── CASE.md
├── ARQUITETURA.md
├── AI_USAGE.md
├── README.md
├── docker-compose.yml
├── .pre-commit-config.yaml
├── .github/workflows/ci.yml
│
├── docs/
│   ├── er-diagram.md            # Mermaid
│   ├── c4-context.md            # Mermaid
│   ├── c4-container.md          # Mermaid
│   └── ddl.sql
│
├── backend/
│   ├── Dockerfile
│   ├── pyproject.toml
│   ├── alembic/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py            # pydantic-settings
│   │   ├── database.py          # Engine + Session
│   │   ├── exceptions.py        # Handler global
│   │   │
│   │   ├── models/              # SQLAlchemy models
│   │   ├── schemas/             # Pydantic DTOs
│   │   ├── repositories/       # Queries (ORM + SQL nativo)
│   │   ├── services/           # Lógica de negócio
│   │   │   └── pricing/        # Strategy Pattern
│   │   └── api/v1/             # Rotas
│   │
│   ├── tests/
│   └── CONTEXTO.md
│
└── frontend/
    ├── Dockerfile
    ├── src/
    │   ├── api/                 # Axios tipado
    │   ├── hooks/               # React Query
    │   ├── components/          # UI pura
    │   ├── pages/
    │   └── types/
    ├── tests/
    └── CONTEXTO.md
```

---

## 3. Camadas (Backend)

```
API (rotas + validação)
  │            │
  ▼            ▼ (relatórios: direto pro repo)
Services    Repositories
(negócio)   (SQL nativo)
  │
  ▼
Repositories
(ORM)
```

Relatórios pulam a camada de negócio — vão direto da rota pro repository. É exigência do case.

---

## 4. Modelagem de Dados

5 tabelas. Sem inventar entidade desnecessária.

| Tabela            | Campos-chave                                                                                        |
|-------------------|------------------------------------------------------------------------------------------------------|
| `currencies`      | `id`, `code` (BRL/USD), `name`                                                                      |
| `exchange_rates`  | `id`, `from_currency_id`, `to_currency_id`, `rate NUMERIC(20,8)`, `effective_date`                   |
| `receivable_types`| `id`, `name`, `spread_rate NUMERIC(10,6)`                                                            |
| `cedentes`        | `id`, `name`, `document` (CNPJ)                                                                     |
| `transactions`    | `id`, `cedente_id`, `receivable_type_id`, `face_value`, `present_value`, `currency_id`, `payment_currency_id`, `exchange_rate_used`, `term_months`, `base_rate`, `spread_applied`, `status`, `version` (optimistic lock), `created_at` |

**Regras:**
- Valores monetários: `NUMERIC(20,8)` no banco, `Decimal` no Python. Zero `float`.
- `version` na transactions: optimistic locking. Update faz `WHERE version = :v`, se 0 rows → 409.

---

## 5. Endpoints

| Método | Rota                         | O que faz                          |
|--------|------------------------------|------------------------------------|
| GET    | `/api/v1/currencies`         | Lista moedas                       |
| GET    | `/api/v1/exchange-rates`     | Taxa atual                         |
| POST   | `/api/v1/exchange-rates`     | Cria/atualiza taxa                 |
| GET    | `/api/v1/receivable-types`   | Lista tipos + spreads              |
| POST   | `/api/v1/simulate`           | Calcula VP sem persistir           |
| POST   | `/api/v1/transactions`       | Liquida transação (ACID)           |
| GET    | `/api/v1/transactions/:id`   | Detalhe                            |
| GET    | `/api/v1/reports/statements` | Extrato filtrado + paginação       |

Filtros do extrato: `date_from`, `date_to`, `cedente_id`, `currency_code`, `page`, `page_size`.

---

## 6. Strategy Pattern (Precificação)

```python
# Fórmula: VP = Valor Face / (1 + Taxa Base + Spread) ^ Prazo

class PricingStrategy(ABC):
    @abstractmethod
    def get_spread(self) -> Decimal: ...

    def calculate_present_value(self, face_value, base_rate, term_months) -> Decimal:
        return face_value / (1 + base_rate + self.get_spread()) ** term_months

class DuplicataStrategy(PricingStrategy):
    def get_spread(self) -> Decimal:
        return Decimal("0.015")  # 1.5% a.m.

class ChequeStrategy(PricingStrategy):
    def get_spread(self) -> Decimal:
        return Decimal("0.025")  # 2.5% a.m.
```

Cross-currency: calcula VP na moeda do título, depois converte pra moeda de pagamento usando a taxa do dia.

---

## 7. Frontend

Três telas, sem complexidade desnecessária:

1. **Simulação** — formulário com inputs (valor, vencimento, tipo, moedas), chama `/simulate` com debounce, mostra VP em tempo real.
2. **Transações** — grid com TanStack Table, paginação server-side, filtros.
3. **Relatórios** — extrato filtrado por período/cedente/moeda.

**Arquitetura:** componentes recebem props e emitem eventos. Hooks fazem fetch via React Query. Camada `api/` tipada com Axios.

---

## 8. Checklist Sênior (o que entrego)

### Júnior (base)
- [x] API + Frontend rodando
- [x] Cálculo correto
- [x] Banco normalizado + ER
- [x] README com setup

### Pleno (acumulativo)
- [x] Docker Compose
- [x] Exception handler global
- [x] Validação de input (Pydantic)
- [x] Testes unitários (strategies)
- [x] Conventional Commits
- [x] PRs simulados

### Sênior (acumulativo)
- [x] Pre-commit hooks (ruff lint + testes)
- [x] Tag `v1.0.0`
- [x] Diagrama C4 nível 1 e 2 (Mermaid em `/docs`)
- [x] Logs estruturados (structlog JSON)
- [x] CI pipeline (GitHub Actions: lint + test)
- [x] Retry simples na chamada mockada de câmbio
- [x] Optimistic locking em transactions

---

## 9. O que NÃO faço (e por quê)

Estas são evoluções naturais. Ficam mencionadas no README como melhorias futuras:

- **Prometheus/Grafana** — logs estruturados já cobrem o obrigatório. Métricas são próximo passo.
- **Circuit Breaker** — retry simples basta pra uma chamada mockada.
- **Tracing distribuído** — monolito, não precisa agora.
- **Autenticação/RBAC** — case não pede.
- **Deploy real** — case pede local.
- **Frontend polido** — funcional e limpo. Design system seria over-engineering.

---

## 10. Git Workflow

**GitHub Flow.** Feature branches saem de `main`, voltam via PR.

```
main ──────────────────────────────────►
  ├── feature/infra-setup ──────► PR
  ├── feature/currency-engine ──► PR
  ├── feature/pricing-strategy ─► PR
  ├── feature/transactions ─────► PR
  ├── feature/reports ──────────► PR
  ├── feature/frontend ─────────► PR
  └── feature/observability ────► PR
```

Commits: `feat(pricing): add duplicata strategy`
Tag final: `v1.0.0`

---

## 11. Docker Compose

```yaml
services:
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: srm_credit
      POSTGRES_USER: srm
      POSTGRES_PASSWORD: srm_secret
    ports: ["5432:5432"]
    volumes: [pgdata:/var/lib/postgresql/data]

  backend:
    build: ./backend
    ports: ["8000:8000"]
    depends_on: [db]
    environment:
      DATABASE_URL: postgresql+asyncpg://srm:srm_secret@db:5432/srm_credit

  frontend:
    build: ./frontend
    ports: ["5173:5173"]
    depends_on: [backend]

volumes:
  pgdata:
```

`docker-compose up --build` — pronto.

---

## 12. Regras pro Agente

1. `Decimal` sempre. Zero `float`.
2. Transações ACID — `async with session.begin()`.
3. Pydantic valida na borda. Service assume dado limpo.
4. HTTP status corretos: 400, 404, 409, 422, 500.
5. Relatórios usam `text()` do SQLAlchemy, não ORM.
6. Testes com valores calculados na mão.
7. structlog com `request_id` em todo log.
8. Commits atômicos, Conventional Commits.
9. Sem `any` no TypeScript.
10. Componentes não fazem fetch. Hooks fazem fetch.

---

## 13. Ordem de Implementação

| #  | O que                        | Branch                       |
|----|------------------------------|------------------------------|
| 1  | Docker + banco + FastAPI base | `feature/infra-setup`        |
| 2  | Models + Alembic + DDL       | `feature/data-models`        |
| 3  | Câmbio (CRUD + retry)        | `feature/currency-engine`    |
| 4  | Pricing (Strategy + testes)  | `feature/pricing-strategy`   |
| 5  | Transações (ACID + lock)     | `feature/transactions`       |
| 6  | Relatórios (SQL nativo)      | `feature/reports`            |
| 7  | Frontend completo            | `feature/frontend`           |
| 8  | Logs + CI + hooks            | `feature/observability`      |
| 9  | Docs (C4, ER, AI_USAGE)     | `docs/architecture`          |
