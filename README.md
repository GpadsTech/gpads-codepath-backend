# GPADS CodePath — API Django

Implementação incremental do backend recebido. Fluxo: atividade → entrega → avaliação manual → pontos no Firestore → publicação GitHub → ranking/dashboard.

**Estado:** implementação e testes locais concluídos; homologação com Firebase, GitHub e frontend reais pendente. Não é uma declaração de prontidão para produção. Consulte `AUDIT.md`, `API_CONTRACT.md` e `VALIDATION.md`.

## Stack e execução (Windows/PowerShell)

Python 3.12 recomendado, Django 5.2, DRF, Firebase Admin SDK, Cloud Firestore, Firebase Authentication, requests, django-cors-headers, serializers DRF, pytest e pytest-django. O SQLite existente continua apenas para aplicações auxiliares do Django; nenhuma entidade de negócio é gravada nele.

Na pasta `backend` extraída:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Copie a chave gerada para `DJANGO_SECRET_KEY` no `.env`. Preencha as variáveis abaixo. Se a política do PowerShell impedir a ativação, use `.\.venv\Scripts\python.exe` no lugar de `python`; não é necessário mudar a política da máquina.

```powershell
python manage.py check
python manage.py migrate
python -m pytest -v
python manage.py runserver 127.0.0.1:8000
```

`migrate` atende somente às tabelas auxiliares Django. Não cria coleções Firestore. O health check não depende de credenciais e deve retornar:

```json
{"status":"ok","message":"GPADS Backend está funcionando!"}
```

Acesse `http://127.0.0.1:8000/api/health/`. O servidor de desenvolvimento não é servidor de produção. Em implantação, configure hosts, HTTPS, segredo estável e servidor WSGI/ASGI.

## Variáveis de ambiente

| Variável | Uso |
|---|---|
| `DJANGO_SECRET_KEY` | Segredo estável para implantação. Sem valor, uma chave efêmera permite checks locais, mas não deve ser usada em implantação. |
| `DJANGO_DEBUG` | `False` por padrão; não habilitar em produção. |
| `DJANGO_ALLOWED_HOSTS` | Hosts separados por vírgula, sem protocolo. |
| `FRONTEND_URL` | Origem CORS exata, padrão `http://localhost:5173`. |
| `FIREBASE_CREDENTIALS_PATH` | Caminho absoluto ou relativo à pasta backend, fora do versionamento. Se omitido, usa Application Default Credentials. |
| `FIREBASE_PROJECT_ID` | Projeto Firebase, opcional quando inferível da credencial. |
| `GITHUB_TOKEN` | Token somente no servidor, com Contents: read/write nos repositórios permitidos. |
| `GITHUB_OWNER` | Organização/proprietário usado quando a requisição informa só o nome do repositório. |
| `GITHUB_ALLOWED_REPOSITORIES` | Lista exata `org/repo,org/outro`, sem espaços. Vazia bloqueia publicações. |

## Firebase e provisionamento

Ative Authentication (email/senha) e Cloud Firestore. A conta de serviço precisa das permissões de Firestore e da verificação de usuários necessária para `check_revoked=True`. O SDK é inicializado sob demanda. O backend verifica assinatura, expiração e revogação pelo Firebase Admin SDK; o UID vem do token, nunca do payload.

Crie previamente usuários no Firebase Authentication e documentos `users/{UID}` no Firestore por um operador confiável. Não existe endpoint público de cadastro administrativo, mudança de papel ou atribuição de célula. Tokens válidos sem perfil retornam 401. UID de publicação deve usar letras, números, `_` ou `-` (UIDs padrão Firebase são compatíveis).

Estudante:

```json
{"name":"Estudante","email":"estudante@example.com","role":"student","cellId":"aplicacoes","level":1}
```

Líder:

```json
{
  "name":"Líder",
  "email":"lider@example.com",
  "role":"leader",
  "ledCellIds":["aplicacoes"],
  "publicationTargets":{"organizacao/repositorio":["atividades/aplicacoes"]},
  "level":1
}
```

`user` é alias legado de `student`. `leader`, `evaluator` e `admin` somente avaliam células presentes em `ledCellIds`. Admin gerencia desafios, mas não ganha acesso universal a entregas. Autoavaliação é bloqueada. Na finalização, a célula atual do aluno também deve coincidir com a célula registrada na entrega. Se o aluno mudar de célula, um operador deve resolver o vínculo da entrega antes de avaliar; não há migração silenciosa.

Regras de cliente Firestore devem impedir acesso direto aos dados administrativos e pontuações. Há um exemplo conservador `firestore.rules` que nega todo acesso de SDK cliente; Firebase Admin usa IAM e não depende dessas regras. Não substitua regras de um projeto compartilhado sem revisar as outras aplicações.

## Arquitetura e classes

Controller → Service → interface Repository → Firebase Repository → Firestore. `Container` é a composição das dependências. Controllers tratam HTTP e serializers; Services implementam políticas; repositories só leem e persistem dados. O cliente GitHub não conhece pontos.

| Classe | Responsabilidade |
|---|---|
| `FirebaseAuthentication` / `AuthService` | Cabeçalho Bearer, verificação de token e perfil confiável. |
| `UserService` | Perfil autorizado; somente nome pode ser editado via PATCH. |
| `ChallengeService` | Atividades e desativação lógica, sem pontos automáticos. |
| `ReportService` | Submissão, visibilidade e correção com histórico. |
| `EvaluationService` | Autorização atual e finalização transacional. |
| `PointsService` | Validação 0–100, construção do registro e soma do histórico. |
| `FirebaseUnitOfWork` | Transação Firestore com callback reexecutável e leituras anteriores às escritas. |
| `GitHubService` | Destinos autorizados, lease e estados recuperáveis. |
| `GitHubClient` / `GitHubMapper` | HTTP com timeout e transformação em arquivos. |
| `RankingService` | Total derivado do ledger, empates e filtro semanal. |
| `DashboardService` / `LevelPolicy` | Agregação e preservação do nível cadastrado. |

POO: entidades dataclass, serviços compostos e encapsulamento do transporte/persistência. SOLID: responsabilidades separadas, Protocols substituíveis por fakes, injeção de dependências e política de nível isolada. Os testes executam as mesmas regras de negócio com repositories em memória. Clean Code: validação central, erros sanitizados, estados explícitos, funções pequenas e nomes do contrato. Os callbacks de transação não fazem chamadas HTTP.

Árvore completa com indicação de arquivos adicionados/modificados/removidos: `CHANGES.md`.

## Firestore e integridade

- `users/{uid}`: perfil, `role`, `cellId`, `ledCellIds`, `publicationTargets`, `level`. O `id` é sempre a chave do documento. `uid` é exposto como alias no perfil HTTP. Um campo legado `points` é ignorado na soma: a fonte é o ledger.
- `challenges/{id}`: título, descrição, status active/inactive, dificuldade, célula opcional e data UTC. `points` é aceito como metadado legado (0–100), sem efeito na avaliação.
- `reports/{id}`: studentId, challengeId, cellId (snapshot), description, report, code, status, submittedAt, revision, history, evaluation e github.
- `points/{reportId}`: id determinístico da entrega, studentId, challengeId, reportId, activityId/submissionId (aliases da documentação), points, evaluatedBy, createdAt, source=evaluation.

IDs novos são UUID hex; timestamps novos são strings ISO 8601 UTC com `Z`. Dados legados com tipos diferentes precisam ser normalizados antes de uso. Models dataclass representam os documentos e serializers validam requisições; não há models SQL de negócio.

Avaliação aprovada e pontos são persistidos **na mesma transação**. Uma leitura da entrega e do registro de pontos precede a escrita; concorrentes recebem conflito após retry do SDK. `EVALUATED` é final. Nota zero é válida. O total é calculado pelo ledger, evitando divergência com saldo materializado.

Devolução marca `REJECTED` e exige feedback; não gera pontos. Reenvio mantém o ID, incrementa revision, preserva conteúdo/feedback anterior em history e volta para `PENDING_EVALUATION`. Cada submissão aceita texto de relatório, código ou ambos. Não executa o código recebido.

## GitHub e recuperação

O destino precisa passar por duas permissões: allowlist do servidor e `publicationTargets` do avaliador. Prefixos têm limite de segmento: `atividades/a` não autoriza `atividades/abc`. Caminhos absolutos, traversal, percent encoding, barras invertidas e segmentos iniciados por ponto são recusados.

Arquivos gerados:

```text
{path}/{studentId}/{reportId}/report.md
{path}/{studentId}/{reportId}/code.txt
```

O sufixo exclusivo protege entregas de estudantes e atividades diferentes. A integração usa a branch padrão do repositório existente. Código é publicado como texto; não cria workflows nem executa arquivos. Não recebe uploads binários, URLs remotas para download, arquivos `files[]` ou ZIP de código.

Fluxo: PENDING → PROCESSING → GITHUB_PUBLISHED → COMPLETED. Falha técnica GitHub → GITHUB_ERROR. Lease de cinco minutos com token de propriedade impede que duas tentativas normais publiquem a mesma entrega simultaneamente. Após expiração, nova tentativa pode recuperar uma execução interrompida; o SHA de cada arquivo protege também a repetição após timeout ou falha parcial. Arquivo existente com conteúdo divergente causa erro e nunca é sobrescrito silenciosamente.

Firestore e GitHub não formam uma transação distribuída. A avaliação permanece concluída e pontuada quando GitHub falha. O endpoint de avaliação retorna 200 com `github.status=GITHUB_ERROR` nesse caso; a UI deve comunicar a falha de publicação. Se o Firestore falhar ao salvar um checkpoint, pode retornar 500 mesmo após efeito externo: consulte a entrega e repita `/publish/`, nunca a avaliação.

Para repetir: `POST /api/reports/{id}/publish/` com `{}` e token de líder autorizado. COMPLETED é no-op; GITHUB_PUBLISHED conclui sem novo HTTP; PROCESSING não expirado retorna 409. Não há worker automático nem retentativa infinita. Permissões são verificadas novamente em cada tentativa. Mudanças posteriores de conteúdo remoto não são auditadas por uma chamada já COMPLETED.

## Ranking, dashboard e decisões explícitas

Ranking geral por padrão. `?period=week` considera segunda-feira 00h até agora em America/Sao_Paulo. Empates compartilham posição (1,1,3), com UID como desempate de exibição. Somente student/user participam; nomes, pontos e nível são visíveis aos autenticados, sem emails. Ranking não tem coleção própria.

Não há fórmula oficial de níveis: `LevelPolicy` conserva `users.level` ou 1. `progress` no dashboard é percentual de atividades visíveis com pelo menos uma entrega avaliada, não avanço de nível. Não implica que a pontuação seja automática. Campos adicionais detalhados em `API_CONTRACT.md`.

## Frontend React + Vite

O frontend usa Firebase Auth e envia **ID Token**, não token de acesso OAuth nem credencial Admin:

```javascript
import { getAuth } from "firebase/auth";

export async function api(path, options = {}) {
  const user = getAuth().currentUser;
  if (!user) throw new Error("Faça login.");
  const token = await user.getIdToken();
  const response = await fetch(`${import.meta.env.VITE_API_URL}/api${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
      Authorization: `Bearer ${token}`,
    },
  });
  const body = await response.json();
  if (!response.ok) throw new Error(body.error?.message ?? "Falha na API");
  return body.data;
}

const submission = await api("/reports/", {
  method: "POST",
  body: JSON.stringify({challengeId: "ID", description: "Entrega", report: "Meu relatório", code: ""}),
});
```

Defina `VITE_API_URL=http://127.0.0.1:8000` no frontend e `FRONTEND_URL` com a origem efetiva do Vite. Tokens GitHub e credenciais Firebase Admin nunca devem usar prefixo VITE_. Trate 401 como sessão inválida, 403 como permissão insuficiente e 409 como necessidade de recarregar o estado. Depois da avaliação, atualize dashboard/ranking e confira o estado GitHub.

## Testes e limitações

```powershell
python manage.py check
python -m pytest -v
```

Testes offline impedem conexões reais ao Firebase e requests. Um teste de emulador é opt-in, limitado a loopback e projeto `demo-codepath-tests`:

```powershell
# Inicie previamente um Firestore Emulator local em 127.0.0.1:8080.
$env:FIRESTORE_EMULATOR_HOST="127.0.0.1:8080"
$env:RUN_FIRESTORE_EMULATOR_TESTS="1"
python -m pytest -m emulator -v
```

Não executado neste ambiente. A concorrência foi testada com UnitOfWork em memória; atomicidade do SDK foi verificada por contrato com mocks, não com emulador real.

Limitações reais: listas e ranking leem coleções completas (adequado apenas ao MVP pequeno; paginação e consultas indexadas são evolução necessária); publicação síncrona; sem armazenamento binário; histórico embutido limitado com entrega a 800 KB UTF-8 serializados; sem recálculo de níveis; sem política oficial de prazo quinzenal ou unicidade aluno/atividade (múltiplas entregas distintas são permitidas e cada avaliação pontua); sem ajuste administrativo de avaliações finalizadas; provisionamento e migração de documentos são manuais. A integridade garantida é por ID de entrega, não deduplicação semântica de duas submissões diferentes.

## Referências técnicas consultadas

- https://firebase.google.com/docs/firestore/manage-data/transactions
- https://firebase.google.com/docs/firestore/transaction-data-contention
- https://docs.github.com/en/rest/repos/contents?apiversion=2022-11-28
