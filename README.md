# GPADS CodePath — Backend

Backend responsável pelas regras de negócio, autenticação, persistência de dados, pontuação, ranking, dashboard e integração com o GitHub da plataforma **GPADS CodePath**.

O projeto utiliza **Django + Django REST Framework + Firebase Firestore**, seguindo uma arquitetura organizada em camadas para facilitar manutenção, testes e integração com o frontend.

---

# 1. Visão geral do sistema

A plataforma tem como objetivo acompanhar as atividades realizadas pelos estudantes, receber suas entregas, permitir que um avaliador analise essas entregas e atribua pontos.

O fluxo principal é:

```text
ESTUDANTE
    │
    │ realiza atividade
    ▼
ENVIA RELATÓRIO / CÓDIGO
    │
    ▼
BACKEND DJANGO
    │
    ▼
ENTREGA REGISTRADA
    │
    ▼
AVALIADOR / ADMIN
    │
    │ analisa a entrega
    │ define os pontos
    ▼
AVALIAÇÃO
    │
    ├──────────────────────┐
    ▼                      ▼
FIRESTORE                GITHUB
    │                      │
    │                      ├── Repositório escolhido
    │                      ├── Pasta escolhida
    │                      └── Relatório / código
    │
    └── Pontos do estudante
        + histórico
        + atividade
        + avaliação
        + referência da entrega
```

## Regra fundamental da gamificação

**O GitHub não determina os pontos.**

Os pontos são definidos manualmente pelo avaliador depois que a entrega do estudante é analisada.

O Firestore é responsável por armazenar os pontos e o histórico de pontuação.

O GitHub é utilizado para armazenar ou registrar a entrega do estudante, como código e/ou relatório, no repositório e na pasta definidos pelo avaliador.

---

# 2. Tecnologias

## Backend

* Python
* Django
* Django REST Framework
* Firebase Admin SDK
* Firebase Firestore
* Firebase Authentication
* Pytest
* Pydantic / validação de dados
* django-cors-headers

## Integrações

* GitHub API

## Frontend

O backend será consumido pelo frontend desenvolvido em:

* React
* Vite

O frontend não deve acessar o Firestore diretamente para executar regras de negócio.

O fluxo esperado é:

```text
React
  ↓
HTTP / REST / JSON
  ↓
Django
  ↓
Service
  ↓
Repository
  ↓
Firestore
```

Para operações relacionadas ao GitHub:

```text
React
  ↓
Django API
  ↓
Service
  ↓
GitHub Integration
  ↓
GitHub
```

---

# 3. Arquitetura do backend

A arquitetura segue separação de responsabilidades.

```text
Frontend
    │
    ▼
Controllers
    │
    ▼
Services
    │
    ▼
Repository Interfaces
    │
    ▼
Firebase Repositories
    │
    ▼
Firestore
```

Para integrações externas:

```text
Services
    │
    ▼
Integration Layer
    │
    ▼
GitHub API
```

## Responsabilidade de cada camada

### Controller

Recebe as requisições HTTP e devolve as respostas para o frontend.

Não deve conter regras complexas de negócio.

Exemplo:

```text
POST /api/points/
        ↓
PointsController
        ↓
PointsService
```

---

### Service

Contém as regras de negócio da aplicação.

É onde devem ficar operações como:

* validar dados;
* verificar permissões;
* processar avaliações;
* calcular informações do ranking;
* registrar pontos;
* coordenar uma entrega para o GitHub;
* coordenar operações entre Firestore e GitHub.

O Service não deve conhecer detalhes específicos de como o Firestore salva os documentos.

---

### Repository Interface

Define o contrato que um repositório precisa cumprir.

Exemplo:

```text
PointsRepository
    ├── create()
    ├── find_by_student()
    └── find_history()
```

Isso permite trocar a implementação sem alterar as regras de negócio.

---

### Firebase Repository

Implementa efetivamente a comunicação com o Firestore.

Exemplo:

```text
PointsRepository
        ▲
        │ implementa
        │
FirebasePointsRepository
        │
        ▼
Firestore
```

---

### Models

Representam as entidades utilizadas pelo sistema.

Exemplos:

* User
* Challenge
* Points
* Report

---

### Schemas

Responsáveis pela validação e estrutura dos dados recebidos ou enviados pela API.

---

### Middleware

Responsável por comportamentos que precisam acontecer antes da execução das regras da aplicação.

Neste projeto, o principal uso é autenticação e identificação do usuário.

---

### Exceptions

Centraliza exceções específicas da aplicação.

Isso evita espalhar mensagens e regras de erro pelo código.

---

# 4. Estrutura atual do projeto

A estrutura já criada é:

```text
backend/
│
├── app/
│   │
│   ├── main.py
│   │
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py
│   │   ├── firebase.py
│   │   ├── urls.py
│   │   ├── views.py
│   │   ├── asgi.py
│   │   └── wsgi.py
│   │
│   ├── controllers/
│   │   ├── __init__.py
│   │   ├── user_controller.py
│   │   ├── challenge_controller.py
│   │   ├── points_controller.py
│   │   ├── ranking_controller.py
│   │   └── dashboard_controller.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── user_service.py
│   │   ├── challenge_service.py
│   │   ├── points_service.py
│   │   ├── ranking_service.py
│   │   └── dashboard_service.py
│   │
│   ├── repositories/
│   │   ├── __init__.py
│   │   │
│   │   ├── interfaces/
│   │   │   ├── __init__.py
│   │   │   ├── user_repository.py
│   │   │   ├── challenge_repository.py
│   │   │   ├── points_repository.py
│   │   │   └── report_repository.py
│   │   │
│   │   └── firebase/
│   │       ├── __init__.py
│   │       ├── firebase_user_repository.py
│   │       ├── firebase_challenge_repository.py
│   │       ├── firebase_points_repository.py
│   │       └── firebase_report_repository.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── challenge.py
│   │   ├── points.py
│   │   └── report.py
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user_schema.py
│   │   ├── challenge_schema.py
│   │   ├── points_schema.py
│   │   └── dashboard_schema.py
│   │
│   ├── middleware/
│   │   ├── __init__.py
│   │   └── auth_middleware.py
│   │
│   └── exceptions/
│       ├── __init__.py
│       └── application_exceptions.py
│
├── credentials/
│   └── firebase-service-account.json
│
├── tests/
│   ├── test_firebase.py
│   ├── test_users.py
│   ├── test_challenges.py
│   ├── test_points.py
│   └── test_ranking.py
│
├── .env
├── .env.example
├── .gitignore
├── requirements.txt
├── pytest.ini
└── manage.py
```

---

# 5. Responsabilidade dos arquivos

## `app/main.py`

Ponto de entrada auxiliar da aplicação.

Não deve concentrar regras de negócio.

---

# 6. Configuração

## `app/config/settings.py`

Configurações do Django.

Responsável por:

* aplicações instaladas;
* middleware;
* banco/configurações externas;
* CORS;
* arquivos estáticos;
* configurações de ambiente;
* configurações gerais do projeto.

As credenciais e informações sensíveis devem ser obtidas através do `.env`.

---

## `app/config/firebase.py`

Responsável exclusivamente pela inicialização do Firebase Admin SDK.

Responsabilidades:

* localizar as credenciais;
* inicializar o Firebase;
* disponibilizar o Firestore.

Nenhuma regra de negócio deve ficar neste arquivo.

---

## `app/config/urls.py`

Responsável pelo roteamento das URLs da aplicação.

Exemplo:

```text
/api/health/
/api/users/
/api/challenges/
/api/points/
/api/ranking/
/api/dashboard/
```

---

## `app/config/views.py`

Views/configurações HTTP básicas do projeto.

O endpoint de health check deve continuar disponível para verificar se o backend está funcionando.

Exemplo:

```json
{
    "status": "ok",
    "message": "GPADS Backend está funcionando!"
}
```

---

# 7. Controllers

Os Controllers fazem a ponte entre o HTTP e os Services.

## `user_controller.py`

Responsável por:

* consultar usuário;
* atualizar dados permitidos;
* retornar informações do estudante;
* validar acesso à operação.

Não deve realizar consultas diretamente ao Firestore.

---

## `challenge_controller.py`

Responsável pelas operações relacionadas às atividades/desafios disponibilizados aos estudantes.

Exemplos:

```text
GET
POST
PATCH
DELETE
```

A definição de uma atividade/desafio é diferente da avaliação da entrega.

O Controller não deve atribuir pontos automaticamente quando o estudante conclui uma atividade.

---

## `points_controller.py`

Responsável pelos endpoints relacionados à pontuação.

Pode ser utilizado para:

* consultar pontos do estudante;
* consultar histórico;
* registrar uma avaliação pontuada;
* retornar informações de pontuação para o frontend.

A definição dos pontos deve ocorrer a partir da avaliação realizada pelo avaliador.

---

## `ranking_controller.py`

Responsável por disponibilizar os dados necessários para o ranking.

Exemplo:

```text
GET /api/ranking/
GET /api/ranking/me/
```

---

## `dashboard_controller.py`

Responsável pelos endpoints utilizados pelo dashboard.

Pode reunir informações como:

* total de pontos;
* nível;
* posição no ranking;
* atividades;
* histórico;
* entregas;
* indicadores.

---

# 8. Services

## `user_service.py`

Centraliza as regras de negócio relacionadas aos usuários.

Exemplos:

* buscar estudante;
* atualizar dados;
* validar usuário;
* verificar permissões.

---

## `challenge_service.py`

Centraliza as regras relacionadas às atividades/desafios.

Uma atividade representa aquilo que o estudante deve realizar.

O fato de o estudante realizar a atividade **não significa automaticamente que ele ganhou pontos**.

A pontuação será definida após a avaliação da entrega.

---

## `points_service.py`

É uma das partes mais importantes da gamificação.

Responsável por:

* receber a avaliação aprovada;
* validar a quantidade de pontos;
* identificar o estudante que realizou a entrega;
* registrar os pontos no Firestore;
* manter o histórico;
* impedir inconsistências ou duplicações;
* disponibilizar os dados para ranking e dashboard.

Fluxo:

```text
Entrega do estudante
        ↓
Avaliação
        ↓
Avaliador define pontos
        ↓
PointsService
        ↓
FirebasePointsRepository
        ↓
Firestore
```

---

## `ranking_service.py`

Responsável pelas regras de geração do ranking.

O ranking deve ser derivado dos dados armazenados no Firestore.

Não é necessário criar uma coleção separada de ranking inicialmente.

Exemplo:

```text
Users
 ├── João       500 pontos
 ├── Maria      420 pontos
 └── Pedro      350 pontos
```

O Service organiza esses dados para o frontend.

---

## `dashboard_service.py`

Responsável por reunir os dados necessários para o dashboard.

Pode combinar informações provenientes de:

* usuários;
* atividades;
* pontos;
* avaliações;
* entregas.

---

# 9. Repositories

Os repositories são responsáveis pelo acesso aos dados.

O Service não deve fazer chamadas diretamente ao Firestore.

Exemplo incorreto:

```python
def add_points():
    firestore.collection("points").add(...)
```

Exemplo correto:

```text
PointsService
      ↓
PointsRepository
      ↓
FirebasePointsRepository
      ↓
Firestore
```

---

# 10. Repository Interfaces

## `user_repository.py`

Define o contrato para operações de usuários.

---

## `challenge_repository.py`

Define o contrato para operações de atividades/desafios.

---

## `points_repository.py`

Define o contrato para:

* criar registro de pontuação;
* buscar pontos;
* buscar histórico;
* consultar pontuação por estudante.

---

## `report_repository.py`

Responsável pelo contrato de persistência das entregas/relatórios.

O relatório deve estar relacionado:

```text
Estudante
    ↓
Atividade
    ↓
Entrega
    ↓
Avaliação
```

---

# 11. Firebase Repositories

Os arquivos dentro de:

```text
repositories/firebase/
```

são as implementações concretas dos contratos definidos nas interfaces.

Exemplo:

```text
points_repository.py
        ▲
        │
        │ implementa
        │
firebase_points_repository.py
        │
        ▼
Firestore
```

---

# 12. Models

## `user.py`

Representa o estudante/usuário.

Informações esperadas:

```json
{
    "uid": "firebase_uid",
    "name": "Nome",
    "email": "email",
    "role": "student",
    "points": 0,
    "level": 1
}
```

---

## `challenge.py`

Representa a atividade/desafio que será realizado pelo estudante.

Exemplo:

```json
{
    "id": "activity_001",
    "title": "Implementar tela de ranking",
    "description": "Desenvolver a tela de ranking",
    "status": "active"
}
```

Os pontos **não devem ser considerados automaticamente ganhos apenas porque a atividade existe ou foi concluída**.

---

## `points.py`

Representa um registro de pontuação.

Exemplo:

```json
{
    "studentId": "uid_001",
    "activityId": "activity_001",
    "submissionId": "submission_001",
    "points": 85,
    "evaluatedBy": "uid_admin",
    "createdAt": "timestamp"
}
```

---

## `report.py`

Representa a entrega realizada pelo estudante.

Uma entrega pode conter ou referenciar:

* relatório;
* código;
* arquivos;
* descrição;
* estudante;
* atividade;
* data de envio;
* status da avaliação;
* informações da publicação no GitHub.

---

# 13. Schemas

Schemas definem o formato esperado dos dados.

## `user_schema.py`

Entrada e saída de dados de usuários.

## `challenge_schema.py`

Entrada e saída de atividades.

## `points_schema.py`

Entrada e saída de dados relacionados à pontuação.

## `dashboard_schema.py`

Formato das informações retornadas ao dashboard.

Os schemas devem impedir que o frontend receba estruturas inconsistentes.

---

# 14. Autenticação e autorização

## `auth_middleware.py`

Responsável por identificar o usuário autenticado e permitir que o backend saiba quem está realizando a requisição.

A aplicação possui diferentes níveis de acesso.

### Estudante

Pode:

* visualizar atividades;
* enviar entregas;
* consultar seus pontos;
* consultar seu histórico;
* visualizar ranking;
* visualizar seu dashboard.

### Avaliador/Admin

Pode:

* visualizar entregas dos estudantes;
* avaliar entregas;
* definir a quantidade de pontos;
* publicar/registrar a entrega no GitHub;
* consultar informações administrativas.

O backend deve validar a permissão **no servidor**.

Não é suficiente esconder um botão no frontend.

---

# 15. Fluxo completo da entrega e avaliação

Este é o fluxo principal que deve ser implementado.

## Etapa 1 — Estudante realiza a atividade

O estudante recebe uma atividade existente no sistema.

```text
Challenge
    ↓
Estudante
    ↓
Realiza atividade
```

---

## Etapa 2 — Estudante envia a entrega

O estudante envia:

* relatório;
* código;
* ou ambos.

```text
Estudante
    ↓
POST /api/reports/
    ↓
ReportController
    ↓
ReportService
    ↓
ReportRepository
    ↓
Firestore
```

A entrega inicialmente deve ficar com status semelhante a:

```text
PENDING_EVALUATION
```

---

## Etapa 3 — Avaliador acessa a entrega

O avaliador consulta as entregas pendentes.

```text
GET /api/reports/pending/
```

O backend retorna as entregas disponíveis para avaliação.

---

## Etapa 4 — Avaliador analisa

O avaliador verifica:

* qualidade do código;
* cumprimento da atividade;
* relatório;
* funcionamento;
* critérios definidos para a atividade.

Depois disso, define manualmente a quantidade de pontos.

Exemplo:

```text
Entrega:
Implementação do Ranking

Avaliação:
Aprovada

Pontos:
85
```

---

# 16. Registro dos pontos

Depois da avaliação:

```text
Avaliador
    ↓
define 85 pontos
    ↓
Django
    ↓
PointsService
    ↓
FirebasePointsRepository
    ↓
Firestore
```

Exemplo:

```json
{
    "studentId": "uid_001",
    "activityId": "activity_001",
    "submissionId": "submission_001",
    "points": 85,
    "evaluatedBy": "uid_admin",
    "source": "evaluation",
    "createdAt": "timestamp"
}
```

O registro precisa estar vinculado ao estudante que realizou a entrega.

---

# 17. Integração com GitHub

O GitHub será utilizado para armazenar/registrar a entrega avaliada.

O avaliador poderá definir:

```text
Repositório:
gpads-dashboard

Pasta:
atividades/ranking/joao/
```

O backend será responsável por executar a integração.

Fluxo:

```text
Avaliação aprovada
        ↓
Avaliador define:
- pontos
- repositório
- pasta
        ↓
Django
        ↓
GitHubService
        ↓
GitHub API
        ↓
Repositório
        ↓
Pasta escolhida
        ↓
Relatório / Código
```

A estrutura exata dos arquivos e da operação GitHub deverá ser definida durante a implementação da integração.

---

# 18. Regra importante sobre Firestore e GitHub

Firestore e GitHub são sistemas externos independentes.

Portanto, não devemos assumir que uma operação envolvendo os dois será uma única transação atômica.

O sistema deve possuir um status para acompanhar a operação.

Exemplo:

```text
PENDING
    ↓
PROCESSING
    ↓
GITHUB_PUBLISHED
    ↓
COMPLETED
```

Em caso de erro:

```text
GITHUB_ERROR
```

Isso permite tentar novamente a publicação sem gerar pontos duplicados.

### Regra contra duplicação

O sistema deve conseguir identificar que uma entrega já foi avaliada e/ou publicada.

Uma segunda tentativa de publicação não deve criar uma nova pontuação para o estudante.

---

# 19. Estrutura adicional para a integração GitHub

A estrutura atual não possui ainda a camada específica de integração com GitHub.

Ela deverá ser adicionada sem misturar código da API do GitHub dentro dos Services ou Repositories do Firebase.

Estrutura planejada:

```text
app/
│
├── integrations/
│   └── github/
│       ├── __init__.py
│       ├── github_client.py
│       └── github_mapper.py
```

E, conforme a implementação:

```text
services/
└── github_service.py
```

### `github_client.py`

Responsável pela comunicação técnica com a API do GitHub.

Não deve conter regras de negócio da gamificação.

### `github_mapper.py`

Responsável por transformar os dados internos da aplicação no formato necessário para o GitHub.

### `github_service.py`

Coordena a operação de publicação da entrega.

Exemplo:

```text
EvaluationService
        ↓
GitHubService
        ↓
GitHubClient
        ↓
GitHub API
```

---

# 20. Firestore

A estrutura inicial do banco deverá ser organizada em torno das entidades do sistema.

Conceitualmente:

```text
Firestore
│
├── users
│
├── challenges
│
├── points
│
└── reports
```

O relacionamento lógico será:

```text
users
  │
  └── studentId
          │
          ▼
      challenges
          │
          ▼
       reports
          │
          ▼
      evaluation
          │
          ▼
       points
```

A estrutura final dos documentos poderá ser ajustada durante a implementação, mas os relacionamentos devem ser preservados.

---

# 21. API

A API deve utilizar REST e JSON.

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
        "code": "USER_NOT_FOUND",
        "message": "Usuário não encontrado."
    }
}
```

---

# 22. Status HTTP

Utilizar os códigos HTTP corretamente:

```text
200 OK
201 CREATED
400 BAD REQUEST
401 UNAUTHORIZED
403 FORBIDDEN
404 NOT FOUND
500 INTERNAL SERVER ERROR
```

---

# 23. Endpoints previstos

## Usuários

```http
GET /api/users/{userId}/
PATCH /api/users/{userId}/
```

---

## Atividades

```http
GET /api/challenges/
GET /api/challenges/{challengeId}/
POST /api/challenges/
PATCH /api/challenges/{challengeId}/
DELETE /api/challenges/{challengeId}/
```

---

## Entregas

A camada de entregas deverá ser implementada para representar o fluxo real do sistema.

Exemplo:

```http
POST /api/reports/
GET /api/reports/
GET /api/reports/{reportId}/
GET /api/reports/pending/
```

---

## Avaliação

A avaliação deve representar a ação realizada pelo avaliador.

Exemplo conceitual:

```http
POST /api/reports/{reportId}/evaluate/
```

Payload:

```json
{
    "points": 85,
    "repository": "gpads-dashboard",
    "path": "atividades/ranking/joao/"
}
```

O endpoint deve:

1. verificar autenticação;
2. verificar se o usuário possui permissão para avaliar;
3. localizar a entrega;
4. verificar se ela ainda pode ser avaliada;
5. validar os pontos;
6. registrar a avaliação;
7. registrar os pontos no Firestore;
8. publicar/registrar a entrega no GitHub;
9. armazenar a referência da publicação;
10. retornar o resultado ao frontend.

---

## Pontos

```http
GET /api/users/{userId}/points/
GET /api/users/{userId}/points/history/
```

O registro de pontos não deve ser uma ação livre do estudante.

Os pontos devem surgir de uma avaliação autorizada.

---

## Ranking

```http
GET /api/ranking/
GET /api/ranking/me/
```

---

## Dashboard

```http
GET /api/dashboard/
```

---

# 24. Exemplo do fluxo completo da API

```text
1. Estudante
   ↓
POST /api/reports/

2. Backend
   ↓
Salva entrega

3. Avaliador
   ↓
GET /api/reports/pending/

4. Avaliador analisa

5. Avaliador
   ↓
POST /api/reports/{id}/evaluate/

6. Backend
   ↓
Valida avaliador

7. Backend
   ↓
Registra avaliação

8. Backend
   ├──→ Firestore
   │       └── pontos
   │
   └──→ GitHub
           └── relatório/código

9. Backend
   ↓
Retorna resultado

10. Frontend
   ↓
Atualiza dashboard/ranking
```

---

# 25. Responsabilidades — Carlos

Carlos ficará principalmente responsável pela camada de regras de negócio e pela orquestração das operações.

## Responsabilidades principais

### Services

Trabalhar principalmente em:

```text
user_service.py
challenge_service.py
points_service.py
ranking_service.py
dashboard_service.py
```

E implementar:

```text
submission/report service
evaluation service
github service
```

quando essas partes forem adicionadas.

### Controllers

Responsável principalmente por:

* endpoints;
* validações básicas;
* integração Controller → Service;
* respostas HTTP;
* códigos HTTP.

### Autenticação e autorização

Trabalhar com:

```text
auth_middleware.py
```

e regras como:

```text
student
admin/evaluator
```

### Avaliação

Carlos deve implementar a lógica que coordena:

```text
Entrega
   ↓
Avaliação
   ↓
Pontos
   ↓
GitHub
```

### GitHub

Responsável pela implementação da integração em conjunto com Jonathan:

* definição do contrato;
* GitHubService;
* tratamento de erros;
* fluxo de publicação;
* integração com o frontend.

---

# 26. Responsabilidades — Jonathan

Jonathan ficará principalmente responsável pela persistência, modelos, contratos de Repository e testes.

## Responsabilidades principais

### Models

Trabalhar principalmente em:

```text
user.py
challenge.py
points.py
report.py
```

incluindo os ajustes necessários para representar:

```text
Estudante
Atividade
Entrega
Avaliação
Pontos
```

### Schemas

Trabalhar em:

```text
user_schema.py
challenge_schema.py
points_schema.py
dashboard_schema.py
```

e adicionar schemas necessários para:

* entrega;
* avaliação;
* GitHub.

### Repository Interfaces

Responsável por:

```text
user_repository.py
challenge_repository.py
points_repository.py
report_repository.py
```

e pelos novos contratos que forem necessários.

### Firebase Repositories

Responsável principalmente por:

```text
firebase_user_repository.py
firebase_challenge_repository.py
firebase_points_repository.py
firebase_report_repository.py
```

### Firestore

Garantir que os dados sejam persistidos corretamente.

Principal atenção para:

```text
users
challenges
reports
points
```

### Testes

Responsável por ampliar:

```text
test_users.py
test_challenges.py
test_points.py
test_ranking.py
```

e adicionar testes para:

```text
test_reports.py
test_evaluation.py
test_github.py
```

quando essas funcionalidades forem implementadas.

---

# 27. Trabalho conjunto — Carlos + Jonathan

Algumas partes não devem ser desenvolvidas isoladamente.

Os dois devem definir juntos:

### Contrato da API

Antes de frontend e backend implementarem cada endpoint, definir:

```text
URL
Método HTTP
Payload
Resposta
Erros
Status HTTP
```

### Modelo de entrega

Definir exatamente quais dados representam:

```text
atividade
entrega
avaliação
pontos
GitHub
```

### Integração GitHub

Definir:

```text
repositório
pasta
arquivos
referência da publicação
status
tratamento de erro
```

### Testes de integração

Validar o fluxo:

```text
Estudante
   ↓
Entrega
   ↓
Avaliador
   ↓
Avaliação
   ↓
Pontos
   ↓
GitHub
   ↓
Dashboard
```

---

# 28. Sprint 1 — 05/10/2026 a 11/10/2026

## Objetivo

Consolidar o backend já criado e preparar o fluxo de entrega, avaliação, pontuação e integração com GitHub.

### Carlos

* Revisar Controllers existentes.
* Revisar Services existentes.
* Estruturar o fluxo de avaliação.
* Definir as regras de atribuição de pontos.
* Definir permissões de estudante e avaliador.
* Definir contrato dos endpoints de entrega e avaliação.
* Estruturar a futura `github_service.py`.
* Definir junto com Jonathan o contrato da integração GitHub.

### Jonathan

* Revisar Models existentes.
* Revisar Schemas.
* Revisar Repository Interfaces.
* Revisar Firebase Repositories.
* Estruturar o modelo de `Report/Submission`.
* Estruturar o modelo de avaliação.
* Definir como os pontos ficarão relacionados ao estudante e à entrega.
* Preparar testes unitários.

### Entregáveis

Até **11/10/2026**:

* arquitetura revisada;
* modelo de entrega definido;
* modelo de avaliação definido;
* modelo de pontos definido;
* contrato da API definido;
* contrato da integração GitHub definido;
* testes iniciais preparados.

---

# 29. Sprint 2 — 12/10/2026 a 18/10/2026

## Objetivo

Implementar o fluxo funcional de entrega → avaliação → pontos → GitHub.

### Carlos

Implementar:

* endpoints de entrega;
* fluxo de avaliação;
* validação de avaliador;
* `EvaluationService`;
* `PointsService`;
* `GitHubService`;
* integração dos Controllers com os Services;
* tratamento de erros.

### Jonathan

Implementar:

* persistência das entregas;
* persistência das avaliações;
* persistência dos pontos;
* Firebase Repositories;
* schemas;
* consultas de histórico;
* testes unitários e de integração.

### Trabalho conjunto

Implementar e testar:

```text
POST /reports/
GET /reports/
GET /reports/pending/
POST /reports/{id}/evaluate/
GET /users/{id}/points/
GET /users/{id}/points/history/
```

E a integração:

```text
Evaluation
    ↓
Firestore
    +
GitHub
```

### Entregável

Até **18/10/2026**, deve existir um fluxo funcional em que:

```text
Estudante envia entrega
        ↓
Avaliador acessa
        ↓
Avaliador define pontos
        ↓
Pontos são registrados no Firestore
        ↓
Relatório/código é enviado para o GitHub
        ↓
Resultado retorna para o frontend
```

---

# 30. Sprint 3 — 19/10/2026 a 25/10/2026

## Objetivo

Integração completa, testes e estabilização.

### Carlos

* corrigir problemas dos endpoints;
* finalizar regras de negócio;
* validar autorização;
* validar fluxo de avaliação;
* finalizar integração GitHub;
* padronizar respostas da API;
* tratar erros;
* revisar código.

### Jonathan

* finalizar testes;
* validar persistência;
* testar consultas do ranking;
* testar histórico de pontos;
* verificar duplicação de pontuação;
* validar dados no Firestore;
* revisar Models, Schemas e Repositories.

### Trabalho conjunto

Realizar testes completos:

```text
Login
  ↓
Visualização da atividade
  ↓
Envio da entrega
  ↓
Avaliação
  ↓
Definição de pontos
  ↓
Firestore
  ↓
GitHub
  ↓
Ranking
  ↓
Dashboard
```

### Entregável

Até **25/10/2026**:

* backend integrado;
* fluxo principal funcionando;
* testes executados;
* integração GitHub funcionando;
* Firestore validado;
* API documentada;
* código revisado;
* problemas críticos corrigidos.

---

# 31. 26/10/2026 — Entrega final

O dia **26/10/2026** será reservado para:

* validação final;
* testes de apresentação;
* correção de problemas críticos;
* conferência da integração frontend/backend;
* conferência do GitHub;
* conferência do Firestore;
* preparação da demonstração.

Não deve ser planejada uma funcionalidade grande nova para esse dia.

---

# 32. Como Carlos e Jonathan devem trabalhar com o frontend

O frontend não precisa esperar o backend inteiro ficar pronto.

Primeiro deve existir um contrato.

Exemplo:

```http
POST /api/reports/
```

Request:

```json
{
    "challengeId": "activity_001",
    "description": "Minha entrega",
    "files": []
}
```

Response:

```json
{
    "success": true,
    "data": {
        "id": "report_001",
        "status": "PENDING_EVALUATION"
    }
}
```

O frontend pode desenvolver utilizando esse JSON como mock enquanto o endpoint real está sendo implementado.

---

# 33. Regras importantes de desenvolvimento

## Regra 1 — Não colocar regra de negócio no Controller

Evitar:

```text
Controller
    ↓
consulta Firestore
    ↓
calcula pontos
    ↓
chama GitHub
```

Preferir:

```text
Controller
    ↓
Service
    ↓
Repository / Integration
```

---

## Regra 2 — Não acessar Firestore diretamente no Service

Preferir:

```text
Service
    ↓
Repository Interface
    ↓
Firebase Repository
    ↓
Firestore
```

---

## Regra 3 — GitHub não calcula pontos

Não implementar:

```text
commit = pontos
PR = pontos
arquivo = pontos
```

Isso não faz parte da regra do sistema.

Os pontos vêm da avaliação feita pelo avaliador.

---

## Regra 4 — O estudante não define os próprios pontos

O estudante envia a entrega.

Quem define a pontuação é o avaliador autorizado.

---

## Regra 5 — Não duplicar pontos

Uma entrega avaliada não deve gerar uma segunda pontuação simplesmente porque o processo foi executado novamente.

---

## Regra 6 — Não colocar credenciais no Git

Nunca enviar:

```text
.env
firebase-service-account.json
```

para o GitHub.

O arquivo:

```text
.env.example
```

deve conter somente os nomes das variáveis necessárias.

---

# 34. Git

Antes de criar um Pull Request:

```bash
git pull
```

Criar uma branch específica:

```bash
git checkout -b feature/nome-da-funcionalidade
```

Exemplos:

```text
feature/evaluation-flow
feature/github-integration
feature/points-service
feature/report-submission
```

Fazer commits objetivos:

```text
feat: implementa fluxo de avaliação
feat: adiciona persistência de entregas
feat: implementa integração com github
test: adiciona testes de pontuação
fix: corrige duplicação de pontos
```

Evitar commits genéricos:

```text
teste
coisas
mudanças
final
final2
agora vai
```

---

# 35. Testes

Executar:

```bash
pytest
```

Para um teste específico:

```bash
pytest tests/test_points.py -v
```

Para Firebase:

```bash
pytest tests/test_firebase.py -v
```

Antes de considerar uma funcionalidade pronta:

```text
Código
  ↓
Teste
  ↓
Integração
  ↓
Pull Request
  ↓
Code Review
```

---

# 36. Definition of Done

Uma funcionalidade somente deve ser considerada concluída quando:

* [ ] código implementado;
* [ ] segue a arquitetura definida;
* [ ] Controller não possui regra de negócio indevida;
* [ ] Service contém a regra de negócio;
* [ ] Repository é utilizado para persistência;
* [ ] dados estão validados;
* [ ] tratamento de erros implementado;
* [ ] testes criados;
* [ ] testes executados;
* [ ] API testada;
* [ ] integração com frontend validada;
* [ ] documentação atualizada;
* [ ] código revisado;
* [ ] Pull Request revisado.

Para o fluxo de avaliação:

* [ ] estudante consegue enviar entrega;
* [ ] avaliador consegue visualizar entrega;
* [ ] avaliador consegue atribuir pontos;
* [ ] pontos são registrados no estudante no Firestore;
* [ ] entrega é publicada/registrada no GitHub;
* [ ] repositório escolhido é respeitado;
* [ ] pasta escolhida é respeitada;
* [ ] referência do GitHub é armazenada;
* [ ] não existe duplicação de pontuação;
* [ ] ranking reflete os pontos registrados;
* [ ] dashboard recebe os dados corretos.

---

# 37. Estado atual e próximos passos

A estrutura base do backend já foi criada e testada.

Já estão definidos:

```text
Django
Firebase
Firestore
Controllers
Services
Repositories
Models
Schemas
Middleware
Exceptions
Tests
```

A próxima etapa não é recriar o projeto.

É evoluir a estrutura existente para suportar o fluxo real:

```text
ATIVIDADE
    ↓
ESTUDANTE
    ↓
ENTREGA
    ↓
AVALIAÇÃO
    ↓
PONTOS
    ↓
FIRESTORE
    +
GITHUB
    ↓
RANKING / DASHBOARD
```

A integração com o dashboard e demais fontes externas poderá ser expandida posteriormente, mas o backend deve primeiro garantir que esse fluxo principal esteja sólido.

---

# 38. Objetivo final do backend

Ao final da implementação, o backend deverá permitir que o sistema funcione da seguinte maneira:

```text
1. A atividade existe no sistema.

2. O estudante realiza a atividade.

3. O estudante envia seu relatório/código.

4. O backend registra a entrega.

5. O avaliador acessa a entrega.

6. O avaliador analisa o trabalho.

7. O avaliador define a quantidade de pontos.

8. O backend registra os pontos
   no Firestore para o estudante.

9. O backend registra/publica
   o relatório/código no GitHub,
   no repositório e pasta escolhidos.

10. O backend registra a referência
    da publicação.

11. Os pontos passam a compor
    o histórico do estudante.

12. O ranking é atualizado.

13. O dashboard apresenta
    os dados atualizados.
```

Esse é o fluxo de negócio que deve orientar a implementação do backend até **26/10/2026**.
