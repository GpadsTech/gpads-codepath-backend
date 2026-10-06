# GPADS CodePath — Backend
## Sprint 1 — 05/10/2026 e 06/10/2026

Este documento registra a base técnica e as decisões de domínio necessárias para considerar concluídas as tarefas que anteriormente estavam divididas entre Carlos e Jonathan nos dias 05/10 e 06/10.

A partir de 06/10/2026, essas responsabilidades passam a ser executadas por uma única pessoa.

---

## 1. Stack

- Python
- Django
- Django REST Framework
- Firebase Admin SDK
- Firebase Firestore
- Firebase Authentication
- Pydantic
- Pytest
- django-cors-headers

A lista de dependências original do projeto já contempla Django, DRF, CORS, Firebase Admin, dotenv, Pydantic e pytest.

---

# 2. Regra principal do fluxo

```text
ESTUDANTE
   ↓
REALIZA ATIVIDADE
   ↓
ENVIA RELATÓRIO / CÓDIGO
   ↓
ENTREGA
   ↓
LÍDER DA CÉLULA
   ↓
ANALISA
   ├── devolve → REJECTED
   │
   └── conclui avaliação
          ↓
       EVALUATED
          ↓
      0 a 100 pontos
          ↓
       FIRESTORE
          +
       GITHUB
```

O estudante nunca define os próprios pontos.

A pessoa autorizada a avaliar é o **líder da célula** responsável pelo estudante.

---

# 3. Modelo da entrega

A entrega será representada conceitualmente por:

```json
{
  "id": "report_001",
  "studentId": "uid_001",
  "challengeId": "activity_001",

  "description": "Minha entrega da atividade",

  "report": "...",
  "code": "...",

  "status": "PENDING_EVALUATION",

  "submittedAt": "timestamp",

  "evaluation": null,

  "github": null
}
```

### Regras

- `studentId`: estudante que realizou a entrega.
- `challengeId`: atividade relacionada.
- `description`: descrição da entrega.
- `report`: relatório textual, opcional quando houver código.
- `code`: código da entrega, opcional quando houver relatório.
- Uma entrega deve possuir relatório, código ou ambos.
- `status` inicia em `PENDING_EVALUATION`.
- `evaluation` inicia como `null`.
- `github` inicia como `null`.

---

# 4. Status da entrega

```text
PENDING_EVALUATION
EVALUATED
REJECTED
```

### PENDING_EVALUATION

A entrega foi enviada e ainda não possui avaliação final.

### REJECTED

O líder da célula devolveu a entrega para o estudante.

A devolução não representa a avaliação final.

### EVALUATED

A avaliação final foi concluída.

Uma entrega que chegou a `EVALUATED` não pode ser avaliada novamente.

---

# 5. Avaliação

A avaliação é realizada exclusivamente pelo **líder da célula** responsável pelo estudante.

Exemplo:

```json
{
  "evaluatedBy": "leader_001",
  "points": 85,
  "final": true,
  "feedback": "Boa implementação.",
  "evaluatedAt": "timestamp"
}
```

## Regras

- Somente o líder da célula pode avaliar.
- O líder pode devolver a entrega.
- A devolução resulta em `REJECTED`.
- A avaliação final resulta em `EVALUATED`.
- Uma entrega `EVALUATED` não pode ser avaliada novamente.
- A pontuação pode ser `0`.
- A pontuação máxima é `100`.
- Valores menores que `0` ou maiores que `100` são inválidos.
- Os pontos são vinculados à entrega e ao estudante.
- Uma segunda execução do fluxo não pode gerar pontuação duplicada.

---

# 6. Pontos

Exemplo:

```json
{
  "studentId": "uid_001",
  "activityId": "activity_001",
  "submissionId": "report_001",
  "points": 85,
  "evaluatedBy": "leader_001",
  "source": "evaluation",
  "createdAt": "timestamp"
}
```

Intervalo válido:

```text
0 <= points <= 100
```

Os pontos não são calculados pelo GitHub.

O GitHub não possui qualquer influência sobre a pontuação.

---

# 7. Status da publicação no GitHub

```text
PENDING
PROCESSING
GITHUB_PUBLISHED
COMPLETED
GITHUB_ERROR
```

### PENDING

A publicação ainda não começou.

### PROCESSING

O backend está processando a publicação.

### GITHUB_PUBLISHED

O GitHub confirmou a publicação.

### COMPLETED

Todo o fluxo de avaliação/publicação foi concluído.

### GITHUB_ERROR

O GitHub falhou.

Nesse caso o backend deve armazenar o erro e retornar uma mensagem adequada ao frontend.

A falha do GitHub **não deve criar uma nova avaliação nem uma nova pontuação**.

---

# 8. Contrato da API

## Padrão de sucesso

```json
{
  "success": true,
  "data": {}
}
```

## Padrão de erro

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Mensagem do erro."
  }
}
```

---

## 8.1 Criar entrega

```http
POST /api/reports/
```

### Request

```json
{
  "studentId": "uid_001",
  "challengeId": "activity_001",
  "description": "Minha entrega",
  "report": "Meu relatório",
  "code": "Meu código"
}
```

### Response

```json
{
  "success": true,
  "data": {
    "id": "report_001",
    "studentId": "uid_001",
    "challengeId": "activity_001",
    "status": "PENDING_EVALUATION"
  }
}
```

### Status

```text
201 CREATED
400 BAD REQUEST
401 UNAUTHORIZED
```

---

## 8.2 Listar entregas

```http
GET /api/reports/
```

### Status

```text
200 OK
401 UNAUTHORIZED
```

---

## 8.3 Consultar entrega

```http
GET /api/reports/{reportId}/
```

### Status

```text
200 OK
401 UNAUTHORIZED
404 NOT FOUND
```

---

## 8.4 Listar entregas pendentes

```http
GET /api/reports/pending/
```

Retorna somente:

```text
PENDING_EVALUATION
```

### Status

```text
200 OK
401 UNAUTHORIZED
403 FORBIDDEN
```

---

# 9. Avaliar entrega

```http
POST /api/reports/{reportId}/evaluate/
```

### Request

```json
{
  "points": 85,
  "repository": "gpads-dashboard",
  "path": "atividades/ranking/joao/",
  "feedback": "Boa implementação."
}
```

### Regras

Antes da avaliação final o backend deve:

1. identificar o usuário autenticado;
2. verificar se ele é o líder da célula responsável;
3. localizar a entrega;
4. verificar se ela ainda pode ser avaliada;
5. validar `0 <= points <= 100`;
6. registrar a avaliação;
7. registrar os pontos;
8. preparar a publicação no GitHub;
9. retornar o resultado.

Uma entrega `EVALUATED` deve retornar erro se houver tentativa de nova avaliação.

---

# 10. Devolução da entrega

A devolução não é uma avaliação final.

Resultado:

```text
PENDING_EVALUATION
        ↓
      REJECTED
```

A API final para devolução será definida junto com a implementação do fluxo de avaliação na Sprint 2.

---

# 11. Pontos

```http
GET /api/users/{userId}/points/
GET /api/users/{userId}/points/history/
```

O estudante pode consultar seus próprios pontos.

O registro de pontos não deve ser uma ação livre do estudante.

Os pontos surgem exclusivamente de uma avaliação autorizada.

---

# 12. GitHub — contrato da Sprint 1

Nesta Sprint 1 **não será configurado o GitHub API**.

Foi definida somente a separação arquitetural:

```text
app/
└── integrations/
    └── github/
        ├── __init__.py
        ├── github_client.py
        └── github_mapper.py
```

E futuramente:

```text
app/
└── services/
    └── github_service.py
```

Fluxo:

```text
EvaluationService
       ↓
GitHubService
       ↓
GitHubClient
       ↓
GitHub API
```

`github_client.py` será responsável pela comunicação técnica.

`github_mapper.py` será responsável por transformar os dados internos no formato necessário para publicação.

`github_service.py` será responsável pela regra de negócio da publicação.

---

# 13. Firestore

Coleções previstas:

```text
users
challenges
reports
points
```

Relacionamento lógico:

```text
users
  ↓
studentId
  ↓
challenges
  ↓
reports
  ↓
evaluation
  ↓
points
```

A avaliação fica registrada dentro da entrega.

Os pontos possuem um registro próprio para permitir histórico e consultas.

---

# 14. Arquitetura

```text
Controller
    ↓
Service
    ↓
Repository Interface
    ↓
Firebase Repository
    ↓
Firestore
```

Para GitHub:

```text
Service
    ↓
GitHub Integration
    ↓
GitHub API
```

### Regra

Controller não acessa Firestore diretamente.

Service não acessa Firestore diretamente.

Service utiliza a interface do Repository.

---

# 15. Arquivos adicionados nesta Sprint

```text
app/
├── models/
│   ├── report.py
│   └── points.py
│
├── schemas/
│   ├── report_schema.py
│   ├── points_schema.py
│   └── github_schema.py
│
├── repositories/
│   └── interfaces/
│       ├── report_repository.py
│       └── points_repository.py
│
├── integrations/
│   └── github/
│       ├── github_client.py
│       └── github_mapper.py
│
└── exceptions/
    └── application_exceptions.py

tests/
├── test_sprint1_models.py
├── test_sprint1_schemas.py
└── test_sprint1_contracts.py
```

---

# 16. Dependências

Instalar:

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scriptsctivate
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Depois:

```bash
pip install -r requirements.txt
```

Executar:

```bash
pytest
```

---

# 17. Firebase

Nesta etapa não é necessário criar a integração funcional completa.

Para a próxima etapa será necessário:

```text
credentials/
└── firebase-service-account.json
```

O arquivo nunca deve ser enviado ao Git.

No `.env`:

```env
FIREBASE_CREDENTIALS_PATH=credentials/firebase-service-account.json
```

---

# 18. GitHub

Nesta etapa:

```text
GitHub API: NÃO CONFIGURADA
GitHub Token: NÃO NECESSÁRIO
OAuth: NÃO NECESSÁRIO
Publicação real: NÃO IMPLEMENTADA
```

Isso será implementado na Sprint 2.

---

# 19. Definition of Done — 05/10 e 06/10

## Carlos + Jonathan — agora responsabilidade única

### Arquitetura

- [x] Responsabilidades das camadas definidas.
- [x] Fluxo Controller → Service → Repository definido.
- [x] Camada de integração externa definida.

### Modelo

- [x] Modelo de entrega definido.
- [x] Modelo de avaliação definido.
- [x] Modelo de pontos definido.
- [x] Status da entrega definidos.
- [x] Status do GitHub definidos.
- [x] Regra de devolução definida.
- [x] Regra de avaliação final definida.
- [x] Regra de 0–100 pontos definida.
- [x] Regra contra duplicação definida.

### Schemas

- [x] Schema de criação da entrega.
- [x] Schema de resposta da entrega.
- [x] Schema de avaliação.
- [x] Schema de pontos.
- [x] Schema de publicação GitHub.

### Repository

- [x] Contrato de ReportRepository.
- [x] Contrato de PointsRepository.

### GitHub

- [x] Contrato do GitHubClient.
- [x] Mapper inicial.
- [x] Estados de publicação.
- [x] Tratamento conceitual de erro definido.
- [ ] API GitHub configurada — Sprint 2.
- [ ] Token GitHub configurado — Sprint 2.
- [ ] Publicação real — Sprint 2.

### Testes

- [x] Teste de status inicial da entrega.
- [x] Teste de pontuação 0.
- [x] Teste de pontuação 100.
- [x] Teste de pontuação inválida.
- [x] Teste de entrega sem relatório/código.
- [x] Teste dos contratos dos repositories.
- [x] Teste do mapper GitHub.

---

# 20. O que NÃO deve ser considerado concluído ainda

Não considerar como concluído em 05/10 e 06/10:

- implementação dos endpoints;
- persistência real das entregas;
- avaliação funcional;
- publicação real no GitHub;
- autenticação completa;
- ranking;
- dashboard;
- integração definitiva com React.

Esses itens pertencem às etapas seguintes da Sprint 1/Sprint 2.

---

# 21. Próximo passo — 07/10

A partir de 07/10:

```text
Models + Schemas
      ↓
Repositories
      ↓
Firebase
      ↓
Services
      ↓
Controllers
      ↓
Endpoints
```

O objetivo é chegar à Sprint 2 com o contrato já estável e começar diretamente a implementação do fluxo:

```text
ENTREGA
   ↓
AVALIAÇÃO
   ↓
PONTOS
   ↓
GITHUB
```
