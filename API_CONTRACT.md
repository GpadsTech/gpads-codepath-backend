# API_CONTRACT — GPADS CodePath

Todas as rotas abaixo estão implementadas. Prefixo `/api/`, barra final obrigatória. JSON UTF-8; Bearer Firebase ID Token em todas exceto health. Campos desconhecidos são rejeitados (400), incluindo studentId, evaluatedBy, role e pontos fora de suas requisições específicas. Não são criados endpoints livres de pontuação.

Sucesso: `{"success":true,"data":...}`. Erro: `{"success":false,"error":{"code":"FORBIDDEN","message":"Acesso não autorizado."}}`. Health preserva o formato antigo. `DELETE` lógico retorna 200 com documento, não 204.

## Rotas, permissões e parâmetros

As listas retornam arrays em `data`, sem paginação. `{id}` representa ID de documento, não índice numérico. Nenhuma rota aceita filtros não documentados.

| Método e URL | Permissão | Request/parâmetro | data / HTTP de sucesso | Erros específicos além dos comuns |
|---|---|---|---|---|
| GET `/api/health/` | Público | Nenhum | `{status:"ok",message:"GPADS Backend está funcionando!"}` / 200 | — |
| GET `/api/auth/me/` | Autenticado | Nenhum | Perfil / 200 | 401 perfil não provisionado |
| GET `/api/users/{userId}/` | Próprio ou líder da célula atual | userId | Perfil / 200 | 404 USER_NOT_FOUND |
| PATCH `/api/users/{userId}/` | Próprio | `{name}` | Perfil atualizado / 200 | 400 INVALID_INPUT, 404 USER_NOT_FOUND |
| GET `/api/challenges/` | Autenticado | Nenhum | Atividades ativas visíveis; admin vê todas / 200 | — |
| GET `/api/challenges/{challengeId}/` | Autenticado com acesso à célula ou admin | challengeId | Atividade, mesmo inativa / 200 | 404 CHALLENGE_NOT_FOUND |
| POST `/api/challenges/` | Admin | ChallengeInput | Atividade / 201 | 400 INVALID_INPUT |
| PATCH `/api/challenges/{challengeId}/` | Admin | Campos parciais de ChallengeInput | Atividade / 200 | 404 CHALLENGE_NOT_FOUND |
| DELETE `/api/challenges/{challengeId}/` | Admin | Nenhum | Atividade com status inactive / 200 | 404 CHALLENGE_NOT_FOUND |
| POST `/api/reports/` | Student/user com célula cadastrada | ReportInput | Entrega / 201 | 404 CHALLENGE_NOT_FOUND, 409 CHALLENGE_INACTIVE, 400 REPORT_TOO_LARGE |
| GET `/api/reports/` | Próprias ou células lideradas | Nenhum | Array de entregas / 200 | — |
| GET `/api/reports/pending/` | Mesma visibilidade | Nenhum | Entregas PENDING_EVALUATION / 200 | — |
| GET `/api/reports/{reportId}/` | Proprietário ou líder da célula da entrega | reportId | Entrega / 200 | 404 REPORT_NOT_FOUND |
| POST `/api/reports/{reportId}/resubmit/` | Proprietário | ReportContent completo | Entrega pendente, revision+1 / 200 | 409 STATE_CONFLICT se não REJECTED; 400 REPORT_TOO_LARGE |
| POST `/api/reports/{reportId}/evaluate/` | Líder autorizado, sem autoavaliação | EvaluationInput | Entrega finalizada ou devolvida / 200 | 409 ALREADY_EVALUATED, 400 INVALID_GITHUB_TARGET, 403 destino proibido |
| POST `/api/reports/{reportId}/publish/` | Líder autorizado da célula | `{}` | Entrega e checkpoint atual / 200 | 409 PUBLICATION_BUSY, PUBLICATION_LEASE_LOST ou STATE_CONFLICT |
| GET `/api/users/{userId}/points/` | Próprio ou líder da célula atual | userId | `{total,level}` / 200 | 404 USER_NOT_FOUND |
| GET `/api/users/{userId}/points/history/` | Mesmo acima | userId | Array de Points / 200 | 404 USER_NOT_FOUND |
| GET `/api/ranking/` | Autenticado | `period=all` ou `week`, opcional | Array RankingEntry / 200 | 400 INVALID_PERIOD |
| GET `/api/ranking/me/` | Autenticado | Mesmo period | RankingEntry ou null para não participante / 200 | 400 INVALID_PERIOD |
| GET `/api/dashboard/` | Autenticado, dados próprios | Nenhum | Dashboard / 200 | — |

Erros comuns a todas as rotas protegidas: 401 INVALID_TOKEN; 403 FORBIDDEN; 400 INVALID_INPUT (payload inválido); 500 PERSISTENCE_ERROR ou INTERNAL_ERROR. Métodos não permitidos retornam 405. Mensagens não contêm respostas brutas de serviços externos. Listas vazias retornam 200 e `[]`.

## Objetos de entrada

`UserPatch`: name obrigatório, texto não vazio até 120 caracteres. Email é somente leitura; alteração deve ser coordenada pelo operador com Firebase Auth.

`ChallengeInput`:

```json
{"title":"Ranking","description":"Implementar ranking","status":"active","difficulty":"medium","cellId":"aplicacoes","points":100}
```

title e description obrigatórios no POST (máximos 200 e 20000); no PATCH são opcionais. status active/inactive; difficulty easy/medium/hard; cellId opcional/null (atividade global), letras/números/_/- até 128. points inteiro 0–100 legado, não concedido automaticamente. Defaults active, medium e 0.

`ReportInput`:

```json
{"challengeId":"ID_ATIVIDADE","description":"Minha entrega","report":"Texto do relatório","code":"print('exemplo')"}
```

challengeId obrigatório (letras/números/_/- até 128); description obrigatório até 2000; report e code textos opcionais até 200000 caracteres cada, default string vazia. Pelo menos um conteúdo não branco. Sem trim do código. Limite agregado de entrega + histórico: 800000 bytes JSON UTF-8. `ReportContent`, usado no reenvio, tem os mesmos campos exceto challengeId; substitui todo conteúdo atual e não move a entrega para outra atividade.

`EvaluationInput` aprovação (decision assume approve se omitido):

```json
{"decision":"approve","points":85,"feedback":"Bom trabalho","repository":"organizacao/repositorio","path":"atividades/aplicacoes"}
```

points é **inteiro JSON** de 0–100 (não string, booleano ou decimal); repository e path obrigatórios na aprovação. repository até 200 caracteres, path até 300, feedback até 10000. Somente destinos permitidos; path pode terminar em `/`, que é normalizada. Nome curto de repositório usa GITHUB_OWNER.

Devolução:

```json
{"decision":"reject","feedback":"Inclua os testes e reenvie."}
```

Feedback não vazio obrigatório; points, repository e path não são aceitos na devolução. Não há concessão de pontos nem GitHub.

## Objetos de resposta

Perfil: `{id,uid,name,email,role,points,level,cellId}`; campos opcionais não cadastrados podem estar ausentes. points sempre derivado de points, level mantém o valor cadastrado ou 1. Não expõe ledCellIds nem publicationTargets.

Atividade: `{id,title,description,createdAt,status,difficulty,cellId,points}`. createdAt UTC ISO 8601. points é metadado legado.

Entrega recém-criada:

```json
{
  "id":"REPORT_ID","studentId":"UID","challengeId":"CHALLENGE_ID","cellId":"aplicacoes",
  "description":"Minha entrega","report":"Texto","code":"",
  "status":"PENDING_EVALUATION","submittedAt":"2026-10-19T22:00:00Z",
  "revision":1,"history":[],"evaluation":null,"github":null
}
```

`evaluation` após aprovação: `{evaluatedBy,createdAt,feedback,decision:"approve",points}`; devolução tem decision reject sem points. `history[]` guarda revision, description, report, code, submittedAt e evaluation da versão anterior. Status possíveis: PENDING_EVALUATION/EVALUATED/REJECTED.

`github`: `{repository,path,status,attempts,leaseId?,leaseUntil?,error?,files?,updatedAt?}`. files é array `{path,sha,url}`. States: PENDING/PROCESSING/GITHUB_PUBLISHED/COMPLETED/GITHUB_ERROR. A resposta pode expor o token de lease (identificador de coordenação, não credencial); nenhum endpoint permite fornecê-lo ou usá-lo para forçar escrita.

**Avaliação com GitHub falhando retorna 200** quando avaliação e pontos foram persistidos: confira github.status. A interface deve oferecer repetição da publicação. Não reenvie a avaliação; EVALUATED retornará 409. Caso receba 500 de persistência, consulte a entrega antes de decidir a próxima ação.

Points:

```json
{"id":"REPORT_ID","studentId":"UID","challengeId":"CHALLENGE_ID","reportId":"REPORT_ID","activityId":"CHALLENGE_ID","submissionId":"REPORT_ID","points":85,"evaluatedBy":"LIDER_UID","createdAt":"2026-10-19T22:00:00Z","source":"evaluation"}
```

RankingEntry: `{position,userId,name,points,level}`. Empates: 1,1,3; UID determina ordem visual. Semana: segunda 00h no fuso America/Sao_Paulo. Sem filtro, pontos de todo o histórico.

Dashboard:

```json
{"points":85,"level":1,"rankingPosition":1,"activities":[],"completedChallenges":1,"pendingReports":0,"evaluatedReports":1,"rejectedReports":0,"progress":0,"history":[]}
```

activities contém desafios visíveis; history contém Points. completedChallenges conta atividades distintas com entrega avaliada; progress mede percentual de atividades visíveis cobertas por avaliação, ou 0 sem atividades. Pode haver atividades históricas concluídas fora da lista ativa. Nível não é calculado com base nesse percentual.

## Chamadas PowerShell

```powershell
$headers = @{ Authorization = "Bearer $idToken" }
Invoke-RestMethod http://127.0.0.1:8000/api/dashboard/ -Headers $headers
$body = @{challengeId="ID"; description="Entrega"; report="Texto"} | ConvertTo-Json
Invoke-RestMethod http://127.0.0.1:8000/api/reports/ -Method Post -Headers $headers -ContentType application/json -Body $body
```

`$idToken` deve vir da sessão Firebase Auth do usuário correto. Não use credencial Admin no cliente. O exemplo React e configuração CORS estão no README.

## Alterações explícitas em relação aos exemplos antigos

`/challenges/{id}/complete/` não existia no código e não foi criado: contradiz a regra atual de pontuação manual. `Report` agora é entrega. Campos `files[]` do exemplo conceitual atualizado não são aceitos: esta implementação adota report/code textuais definidos no pedido, sem simular suporte a anexos binários. Rotas novas compatíveis: `/auth/me/`, `/resubmit/` e `/publish/`. Nenhum contrato de endpoint funcional anterior foi removido; health foi preservado literalmente.
