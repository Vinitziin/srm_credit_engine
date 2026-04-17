# AI_USAGE.md

Documentação do uso de IA na construção do SRM Credit Engine, conforme exigido pela Seção 2 do [CASE.md](CASE.md).

Ferramenta principal: **Claude (Anthropic), modelo Opus 4.7**, via Claude Code (CLI). Autoria intelectual 100% minha — toda linha de código foi lida, compreendida e validada antes do commit.

---

## 1. Como a IA foi usada

O fluxo foi estruturado em 9 fases, cada uma seguindo o ciclo: **plano detalhado → aprovação explícita → commits atômicos na feature branch → merge `--no-ff` em `main`**. Esse ritmo foi definido em [agents.md](agents.md) (regra "§12 — nenhuma linha de código é escrita sem um plano aprovado") e sustentado pela IA sem exceção.

Em cada fase eu atuei como **tech lead**: definia o escopo, aprovava/rejeitava decisões de design, apontava duplicação, revisava diffs. A IA atuou como **executora par**: propunha o plano, fazia perguntas de esclarecimento quando o enunciado era ambíguo, implementava, rodava testes e acusava quando algo estava fora do contrato.

---

## 2. Prompts estratégicos

Os prompts mais impactantes foram os de **alto nível** que ancoravam a filosofia do projeto (em [agents.md](agents.md) e [ARQUITETURA.md](ARQUITETURA.md)), não os táticos. Exemplos dos prompts reais da sessão:

**Entrada da Fase 5 (transações ACID):**
> *"Apresente o plano da Fase 5 per agents.md workflow e aguarde aprovação."*

Isso forçou a IA a ler os PRs anteriores (Fase 4), identificar a duplicação entre `/simulate` e `/transactions` e propor o refactor pro `pricing_service.py` antes de escrever qualquer código. Evitou um monte de retrabalho.

**Aprovação com ajuste (Fase 5):**
> *"Plano aprovado. Um ajuste no ponto 1: o spread duplicado entre as classes e o banco é aceitável agora — o case quer ver o Strategy explícito... adiciona um comentário nas subclasses deixando claro que o valor deve estar em sincronia com a tabela."*

Prompt que ilustra o tradeoff real do case: a duplicação é "DRY-ruim" em teoria mas "didático-bom" na prática — o case pede demonstração do padrão Strategy. A IA inicialmente queria remover a duplicação; eu (humano) decidi mantê-la com comentário explícito.

**Definição de pendências (Fase 7):**
> *"Testes de frontend — sem testes... Modal vs redirect — redirect pra /cedentes... Toasts — react-hot-toast... Formatação pt-BR — sim, Intl com fallback pro currency_code da linha. Lembrete antes de qualquer código: adicionar CORSMiddleware no backend como primeiro commit da branch."*

Respondeu 4 perguntas de esclarecimento de uma vez e adicionou uma instrução cross-fase (CORS antes de começar o frontend). Perguntas específicas → respostas específicas → zero retrabalho.

**Tipos de prompt que mais renderam ao longo da sessão:**

1. **"Apresente o plano e aguarde aprovação"** — forçava reflexão antes de código.
2. **"Aprovado. Respondendo as pendências: [item a item]"** — resolvia ambiguidade em bloco.
3. **"X está errado porque Y"** — correções cirúrgicas com racional, não só "corrija". Permitia à IA entender o princípio e não repetir o erro.

---

## 3. Alucinações e incidentes reais

Três casos concretos dessa sessão onde a IA errou e como foi corrigido:

### 3.1. asyncpg "another operation is in progress" nos testes

A IA gerou um `conftest.py` inicial com fixture de sessão simples (`BEGIN`/`ROLLBACK`). Os testes integration quebraram com `asyncpg.exceptions.InterfaceError: cannot perform operation: another operation is in progress`. A IA inicialmente tentou trocar o transaction mode, sem efeito.

**Causa real:** o pool do engine async do SQLAlchemy mantinha conexões entre event loops do pytest-asyncio (cada teste tem seu próprio loop no modo auto). Conexões asyncpg não cruzam loops.

**Correção (humana + IA em iteração):** `await database.engine.dispose()` em autouse fixture antes E depois de cada teste, forçando reconexão. Nenhum LLM que consultei acertou isso de primeira — foi preciso ler o traceback com calma e lembrar do comportamento do asyncpg.

### 3.2. Ruff `--fix` embaralhando imports

Quando adicionei `import structlog` + `logger = structlog.get_logger()` em [backend/app/api/v1/transactions.py](backend/app/api/v1/transactions.py), coloquei o `logger = ...` abaixo dos imports. O `ruff check --fix` reordenou imports e **deixou o `logger = ...` entre blocos de import**, violando E402 (module-level import not at top). A IA só percebeu porque rodei `ruff check` de novo e vi 3 erros remanescentes.

**Correção:** mover o `logger = ...` para depois de TODOS os imports, não no meio. Lição: `ruff --fix` resolve o que consegue e deixa o resto para humano — não dá pra assumir "está limpo" só porque rodou.

### 3.3. `version: 1` hardcoded no botão de reverter

No primeiro rascunho de `StatementsPage.tsx`, o handler de reverter transação chamava `PATCH /transactions/:id/status` com `version: 1` literal. Funcionaria no caminho feliz (transação recém-criada), mas quebraria ao reverter uma transação já manipulada (version > 1). O DTO do extrato não inclui `version`, então a IA "inventou" o valor.

**Correção:** fetch da transação atual via `GET /transactions/:id` antes do PATCH, pegando a version fresca. Código final em [frontend/src/pages/StatementsPage.tsx:36-48](frontend/src/pages/StatementsPage.tsx).

Pega-se essas três categorias de forma recorrente em projetos com IA: **bug de concorrência não óbvio no traceback**, **ferramenta auto-fixer só parcial**, **alucinação de valor default plausível-mas-errado**.

---

## 4. Análise crítica — onde economizou vs atrapalhou

### Onde economizou muito tempo

- **Scaffolding puro.** Estruturar `pyproject.toml`, `Dockerfile`, `alembic` config, `docker-compose.yml`, hooks de React Query, wrappers axios — tudo gerado corretamente na primeira tentativa. Estimativa: **50-70% do tempo que levaria sozinho nesses pedaços**.
- **Testes.** Subir suite pytest com fixtures async + `httpx.ASGITransport` é chato; a IA entregou o esqueleto completo e só precisei ajustar o isolamento entre testes.
- **DTOs espelhados.** Manter `types/api.ts` em sincronia com os `schemas/*.py` — trabalho mecânico no qual a IA é muito mais rápida e não erra.
- **Documentação.** Este próprio arquivo, README, C4 e ER — gerados em minutos a partir do código real.

### Onde atrapalhou ou cobrou tempo extra

- **Tendência a over-engineering em ambiguidade.** Sem um plano apertado, a IA tende a propor soluções robustas demais (repository pattern com 4 métodos onde 2 bastam, schemas separados para create/update/read quando um serve, tratamento de erro para cenários que não podem acontecer). O antídoto foi aplicar KISS/YAGNI nos prompts de aprovação e rejeitar explicitamente complexidade especulativa.
- **Bugs sutis em concorrência.** Ver 3.1. Para qualquer coisa envolvendo event loops, conexões, locks, a IA precisa de humano com experiência lendo o traceback.
- **"Funciona local" ≠ "funciona no teste".** Algumas vezes a IA declarou uma fase concluída antes de rodar toda a suite integration. Lição: pedir explicitamente `pytest -v` como último passo de cada fase, e ler o output.
- **Commit hygiene.** A IA gostaria de commitar mudanças grandes e abrangentes; foi preciso repetir várias vezes "commits atômicos, um por responsabilidade" e rejeitar diffs mistos.

### Veredito

Para o escopo deste case (feature-completo em ~9 fases, ~60 commits, ~6.000 linhas de código e docs), **a IA foi uma alavanca real de 2-3x** em velocidade — mas só porque o processo humano foi disciplinado: planejamento obrigatório, critério de aprovação explícito, revisão de cada diff, teste após cada fase, e pushback imediato quando algo destoava do estilo do projeto. Sem esse envelope, o output seria mais volumoso e menos coerente.

**O papel do humano não é programar menos — é programar diferente:** menos digitação, mais decisão.
