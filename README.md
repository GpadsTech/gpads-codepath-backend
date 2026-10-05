# README — GPADS Dashboard Gamificada

## Backend — Django + Firebase Firestore

---

# 1. Sobre o sistema

O **GPADS Dashboard Gamificada** é uma plataforma web desenvolvida para apresentar informações e indicadores do GPADS por meio de uma experiência gamificada.

O sistema permitirá que usuários:

* realizem login;
* visualizem seu perfil;
* acompanhem seus pontos;
* completem desafios;
* evoluam de nível;
* acompanhem sua posição no ranking;
* visualizem indicadores e informações do dashboard.

Usuários administradores terão permissões adicionais para:

* cadastrar desafios;
* editar desafios;
* excluir/desativar desafios;
* acompanhar informações gerais;
* visualizar indicadores administrativos.

O sistema será dividido em:

```text
Frontend
React + Vite
        ↓
API REST
        ↓
Backend
Django + Django REST Framework
        ↓
Camada de Serviços
        ↓
Repository Pattern
        ↓
Firebase Admin SDK
        ↓
Firebase Firestore
```

---

# 2. Tecnologias

## Backend

* Python
* Django
* Django REST Framework
* Firebase Admin SDK
* Firebase Authentication
* Firebase Firestore
* Pytest

## Frontend

* React
* Vite
* JavaScript/TypeScript conforme definição da equipe de frontend
* Consumo da API REST

## Arquitetura

O backend deverá seguir:

* Programação Orientada a Objetos;
* SOLID;
* Repository Pattern;
* separação de responsabilidades;
* Services;
* Controllers;
* Schemas;
* tratamento padronizado de erros.

---

# 3. Arquitetura geral

A comunicação deverá seguir obrigatoriamente este fluxo:

```text
┌─────────────────────┐
│      FRONTEND       │
│    React + Vite     │
└──────────┬──────────┘
           │
           │ HTTP / JSON
           ▼
┌─────────────────────┐
│     CONTROLLER      │
│ Recebe a requisição │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│       SERVICE       │
│ Regras de negócio   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ REPOSITORY INTERFACE│
│ Contrato de acesso  │
│ aos dados            │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ FIREBASE REPOSITORY │
│ Implementação       │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│     FIRESTORE       │
│ Banco de dados      │
└─────────────────────┘
```

## Regra importante

Nenhum Controller deverá acessar o Firestore diretamente.

Errado:

```text
Controller → Firestore
```

Correto:

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

Isso permite que as regras de negócio permaneçam separadas da persistência dos dados.

---

# 4. Estrutura do backend

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

# 5. Responsabilidade de cada camada

## 5.1 `config/`

Responsável pelas configurações gerais da aplicação.

### `settings.py`

Configura:

* Django;
* Django REST Framework;
* CORS;
* variáveis de ambiente;
* timezone;
* aplicações instaladas.

Não deve conter regras de negócio.

---

### `firebase.py`

Responsável exclusivamente por:

* carregar as credenciais;
* inicializar o Firebase Admin SDK;
* criar a conexão com o Firestore;
* disponibilizar a instância do Firestore.

Exemplo:

```python
class FirebaseConfig:
    """
    Responsável pela inicialização do Firebase Admin SDK
    e disponibilização do Firestore.
    """
```

---

### `urls.py`

Responsável pelo roteamento das URLs da API.

Exemplo:

```text
/api/users/
/api/challenges/
/api/ranking/
/api/dashboard/
```

Não deve conter regras complexas.

---

# 6. Controllers

Controllers representam a camada HTTP.

Responsabilidades:

* receber requisições;
* extrair parâmetros;
* validar informações básicas;
* chamar o Service;
* retornar HTTP Response;
* utilizar os status HTTP adequados.

O Controller **não deve implementar regras de negócio**.

Exemplo:

```python
class UserController:
    """
    Responsável por receber as requisições HTTP relacionadas
    aos usuários e encaminhá-las para o UserService.
    """
```

---

# 7. Services

Services concentram as regras de negócio.

Exemplo:

```python
class PointsService:
    """
    Responsável pelas regras relacionadas à pontuação.

    Deve:
    - registrar pontos;
    - calcular pontuação;
    - verificar evolução de nível;
    - impedir operações inválidas.
    """
```

Os Services não devem conhecer detalhes de HTTP.

Não devem retornar `JsonResponse`.

---

# 8. Repository Interfaces

As interfaces definem o contrato de persistência.

Exemplo:

```python
class IUserRepository:
    """
    Define o contrato que qualquer implementação de
    persistência de usuários deve seguir.

    A Service conhece esta interface,
    mas não precisa saber que o banco utilizado é Firestore.
    """
```

Exemplo de operações:

```text
get_by_id()
get_all()
create()
update()
delete()
```

---

# 9. Firebase Repositories

São as implementações reais das interfaces utilizando Firestore.

Exemplo:

```python
class FirebaseUserRepository:
    """
    Implementa IUserRepository utilizando Firebase Firestore.

    É responsável exclusivamente pela comunicação
    com a coleção de usuários.
    """
```

O Repository deve saber:

* qual coleção acessar;
* como buscar documentos;
* como criar documentos;
* como atualizar documentos;
* como excluir/desativar documentos.

Não deve decidir regras de negócio.

---

# 10. Models

Representam as entidades do domínio.

Principais entidades:

```text
User
Challenge
Points
Report
```

### User

Representa o usuário da plataforma.

Exemplo:

```json
{
    "name": "Nome do usuário",
    "email": "email@email.com",
    "role": "user",
    "points": 0,
    "level": 1
}
```

---

### Challenge

Representa um desafio.

```json
{
    "title": "Desafio exemplo",
    "description": "Descrição",
    "points": 100,
    "difficulty": "medium",
    "status": "active"
}
```

---

### Points

Representa uma movimentação de pontuação.

```json
{
    "userId": "abc123",
    "challengeId": "challenge01",
    "points": 100,
    "reason": "Desafio concluído"
}
```

---

# 11. Schemas

Schemas definem o formato dos dados recebidos e enviados pela API.

Exemplo:

```python
class UserResponseSchema:
    """
    Define o formato dos dados de usuário
    que poderão ser enviados ao frontend.
    """
```

O objetivo é evitar que o backend envie dados desnecessários ou inconsistentes.

---

# 12. Middleware de autenticação

O `auth_middleware.py` será responsável por validar o token do Firebase Authentication.

Fluxo:

```text
Frontend
   ↓
Firebase Authentication
   ↓
Token
   ↓
Django API
   ↓
Auth Middleware
   ↓
Validação do token
   ↓
Controller
```

O backend deverá identificar:

* UID;
* usuário;
* role/permissão.

Exemplo:

```text
role = user
role = admin
```

---

# 13. Firebase Firestore

O banco principal da aplicação será o **Firebase Firestore**.

Estrutura inicial:

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

## `users`

```text
users/{uid}
```

Exemplo:

```json
{
    "name": "Nathália",
    "email": "usuario@email.com",
    "role": "user",
    "points": 250,
    "level": 3,
    "createdAt": "timestamp"
}
```

---

## `challenges`

```text
challenges/{challengeId}
```

---

## `points`

```text
points/{pointId}
```

---

## `reports`

Será utilizada para os indicadores necessários ao dashboard.

A estrutura definitiva deverá ser definida conforme os indicadores forem fechados.

---

# 14. Ranking

Inicialmente não será criada uma coleção exclusiva para ranking.

O ranking poderá ser obtido através da pontuação dos usuários:

```text
users
   ↓
ordenar por points
   ↓
ranking
```

Isso evita duplicação de informações.

---

# 15. Contrato da API

O contrato da API deve ser definido **antes da implementação completa**.

Isso permite que Alane e Samara desenvolvam o frontend enquanto Carlos e Jonathan desenvolvem o backend.

O frontend não deve precisar esperar o backend inteiro ficar pronto.

---

# 16. Padrão de resposta

Todas as respostas deverão seguir um padrão consistente.

## Sucesso

```json
{
    "success": true,
    "data": {}
}
```

Exemplo:

```json
{
    "success": true,
    "data": {
        "id": "123",
        "name": "Nathália",
        "points": 250,
        "level": 3
    }
}
```

## Erro

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

# 17. Status HTTP

Utilizar corretamente:

```text
200 OK
```

Requisição executada com sucesso.

```text
201 CREATED
```

Recurso criado.

```text
400 BAD REQUEST
```

Dados inválidos.

```text
401 UNAUTHORIZED
```

Usuário não autenticado.

```text
403 FORBIDDEN
```

Usuário autenticado, mas sem permissão.

```text
404 NOT FOUND
```

Recurso não encontrado.

```text
500 INTERNAL SERVER ERROR
```

Erro inesperado no servidor.

---

# 18. Endpoints iniciais

## Usuários

```http
GET /api/users/{userId}/
```

Retorna informações do usuário.

```http
PATCH /api/users/{userId}/
```

Atualiza informações permitidas do usuário.

---

## Desafios

```http
GET /api/challenges/
```

Lista desafios.

```http
GET /api/challenges/{challengeId}/
```

Retorna um desafio específico.

```http
POST /api/challenges/
```

Cria desafio.

```http
PATCH /api/challenges/{challengeId}/
```

Atualiza desafio.

```http
DELETE /api/challenges/{challengeId}/
```

Desativa/exclui desafio conforme a regra definida.

---

## Pontuação

```http
GET /api/users/{userId}/points/
```

Retorna pontuação atual.

```http
GET /api/users/{userId}/points/history/
```

Retorna histórico de pontuação.

---

## Conclusão de desafio

```http
POST /api/challenges/{challengeId}/complete/
```

Responsável por registrar a conclusão do desafio e aplicar os pontos correspondentes.

Exemplo de resposta:

```json
{
    "success": true,
    "data": {
        "challengeId": "challenge01",
        "pointsEarned": 100,
        "totalPoints": 350,
        "level": 4
    }
}
```

---

## Ranking

```http
GET /api/ranking/
```

Retorna ranking geral.

```http
GET /api/ranking/me/
```

Retorna posição do usuário autenticado.

---

## Dashboard

```http
GET /api/dashboard/
```

Retorna os indicadores necessários para o dashboard.

O formato final deverá ser definido em conjunto com Alane e Samara.

---

# 19. Como Carlos e Jonathan devem trabalhar com Alane e Samara

O backend **não precisa estar 100% pronto para o frontend começar**.

O trabalho deverá acontecer através do contrato da API.

Exemplo:

Carlos e Jonathan definem:

```http
GET /api/ranking/
```

Resposta esperada:

```json
{
    "success": true,
    "data": [
        {
            "position": 1,
            "userId": "001",
            "name": "Usuário 1",
            "points": 1000
        },
        {
            "position": 2,
            "userId": "002",
            "name": "Usuário 2",
            "points": 850
        }
    ]
}
```

Alane e Samara podem desenvolver o componente utilizando exatamente essa estrutura, mesmo antes do endpoint existir.

Inicialmente:

```text
Frontend
   ↓
Mock JSON
```

Depois:

```text
Frontend
   ↓
API Django
```

O componente não precisa ser refeito.

---

# 20. Camada de serviço do frontend

Para facilitar a integração, Alane e Samara deverão evitar chamadas HTTP espalhadas pelos componentes.

Exemplo:

```text
frontend/
└── src/
    └── services/
        ├── api.js
        ├── userService.js
        ├── challengeService.js
        ├── rankingService.js
        └── dashboardService.js
```

Assim:

```text
Componente React
       ↓
Service
       ↓
API Django
```

Durante o desenvolvimento:

```text
Componente
       ↓
Service
       ↓
Mock
```

Depois:

```text
Componente
       ↓
Service
       ↓
Django API
       ↓
Firestore
```

---

# 21. Divisão de responsabilidades

## Carlos — Backend / Regras de negócio e API

Carlos ficará principalmente responsável por:

* Controllers;
* Services;
* regras de negócio;
* autenticação;
* autorização;
* middleware;
* endpoints;
* padronização das respostas;
* integração HTTP;
* testes dos Services;
* integração geral da API.

### Principais classes

```text
UserController
UserService

ChallengeController
ChallengeService

PointsController
PointsService

RankingController
RankingService

DashboardController
DashboardService
```

Carlos deverá garantir que a API esteja pronta para ser consumida pelo frontend.

---

# 22. Jonathan — Backend / Dados e Firestore

Jonathan ficará principalmente responsável por:

* Models;
* Schemas;
* Repository Interfaces;
* Firebase Repositories;
* estrutura do Firestore;
* operações CRUD;
* persistência;
* testes dos Repositories;
* configuração relacionada ao acesso aos dados.

### Principais classes

```text
User
Challenge
Points
Report

IUserRepository
IChallengeRepository
IPointsRepository
IReportRepository

FirebaseUserRepository
FirebaseChallengeRepository
FirebasePointsRepository
FirebaseReportRepository
```

Jonathan deverá garantir que os dados possam ser corretamente armazenados e recuperados pelo Service.

---

# 23. Responsabilidades compartilhadas

Carlos e Jonathan deverão trabalhar juntos em:

* definição do contrato da API;
* autenticação;
* integração com Firebase;
* decisões de arquitetura;
* testes de integração;
* correção de bugs;
* revisão de código;
* documentação;
* integração com Alane e Samara.

Nenhum dos dois deve trabalhar isoladamente durante toda a sprint.

O contrato da API deve ser discutido antes da implementação de cada funcionalidade.

---

# 24. Cronograma real do projeto

## Prazo final

**26/10/2026**

Considerando o início efetivo das atividades na segunda-feira, o desenvolvimento será dividido em:

```text
Sprint 1
05/10 → 11/10

Sprint 2
12/10 → 18/10

Sprint 3
19/10 → 25/10

Entrega final
26/10
```

Portanto, não serão utilizadas 8 sprints.

O projeto terá **3 Sprints principais**, cada uma com duração de uma semana, e **26/10 será reservado para fechamento, validação e entrega final**.

---

# 25. SPRINT 1 — Fundação + Contrato da API

## Período

**05/10/2026 → 11/10/2026**

## Objetivo

Criar a base funcional do backend e estabelecer o contrato que permitirá o trabalho paralelo com o frontend.

---

## Carlos

### Tarefas

* Estruturar Controllers.
* Estruturar Services.
* Criar o padrão de respostas da API.
* Definir endpoints iniciais.
* Criar estrutura inicial de autenticação.
* Definir tratamento de erros.
* Criar primeiros endpoints de teste.
* Documentar o contrato inicial.

### Entregáveis

```text
Controllers estruturados
Services estruturados
API Health funcionando
Padrão de resposta definido
Endpoints documentados
Fluxo inicial de autenticação definido
```

---

## Jonathan

### Tarefas

* Configurar Firebase Admin SDK.
* Validar conexão com Firestore.
* Criar Repository Interfaces.
* Criar Firebase Repositories iniciais.
* Definir coleções.
* Criar Models.
* Criar Schemas iniciais.
* Criar testes de conexão.

### Entregáveis

```text
Firebase conectado
Firestore funcionando
Repositories estruturados
Models iniciais
Schemas iniciais
Teste de conexão funcionando
```

---

## Carlos + Jonathan

Até **11/10**, os dois devem entregar juntos:

```text
Contrato inicial da API
        +
Estrutura Firestore
        +
Autenticação definida
        +
Endpoints iniciais documentados
```

---

## Integração com Alane e Samara

Alane e Samara já poderão:

* criar os Services do frontend;
* criar mocks;
* estruturar páginas;
* criar componentes;
* consumir os JSONs definidos no contrato.

Não devem esperar a API completa.

---

# 26. SPRINT 2 — Funcionalidades principais

## Período

**12/10/2026 → 18/10/2026**

## Objetivo

Implementar as principais funcionalidades do sistema e iniciar a integração real entre frontend e backend.

---

## Carlos

### Tarefas

Implementar:

```text
UserService
ChallengeService
PointsService
RankingService
```

Criar endpoints:

```http
GET /api/users/{userId}/
PATCH /api/users/{userId}/

GET /api/challenges/
GET /api/challenges/{challengeId}/
POST /api/challenges/

GET /api/users/{userId}/points/
GET /api/users/{userId}/points/history/

GET /api/ranking/
GET /api/ranking/me/

POST /api/challenges/{challengeId}/complete/
```

Implementar:

* regras de pontuação;
* conclusão de desafios;
* evolução de nível;
* permissões de administrador;
* respostas de erro.

---

## Jonathan

### Tarefas

Implementar os Repositories:

```text
FirebaseUserRepository
FirebaseChallengeRepository
FirebasePointsRepository
```

Implementar:

* criação de usuários;
* consulta de usuários;
* atualização;
* criação de desafios;
* consulta de desafios;
* atualização de desafios;
* registro de pontos;
* consulta do histórico;
* consulta dos usuários para ranking.

---

## Integração com Alane e Samara

Durante essa sprint deverá começar a troca de:

```text
MOCK
 ↓
API REAL
```

A integração deverá acontecer endpoint por endpoint.

Exemplo:

```text
Ranking
↓
Frontend implementado
↓
Contrato validado
↓
Endpoint implementado
↓
Frontend troca mock pela API
↓
Teste
```

Não esperar o backend inteiro ficar pronto para integrar.

---

# 27. SPRINT 3 — Dashboard + Integração final

## Período

**19/10/2026 → 25/10/2026**

## Objetivo

Finalizar o backend, integrar completamente com o frontend e corrigir problemas encontrados.

---

## Carlos

### Tarefas

* Finalizar `DashboardService`.
* Finalizar `DashboardController`.
* Criar endpoint:

```http
GET /api/dashboard/
```

* Finalizar regras de ranking.
* Revisar autenticação.
* Revisar autorização.
* Padronizar respostas.
* Corrigir bugs encontrados na integração.
* Testar todos os endpoints.

---

## Jonathan

### Tarefas

* Finalizar `FirebaseReportRepository`.
* Finalizar estrutura de `reports`.
* Otimizar consultas Firestore.
* Revisar índices necessários.
* Validar consistência dos dados.
* Corrigir problemas de persistência.
* Testar operações do Firestore.
* Apoiar correções encontradas durante a integração.

---

## Carlos + Jonathan

Durante essa sprint:

```text
Backend
   ↕
Frontend
```

deverá ser testado de ponta a ponta.

Devem verificar:

* login;
* autenticação;
* usuário;
* desafios;
* conclusão de desafios;
* pontuação;
* nível;
* ranking;
* dashboard;
* permissões;
* erros;
* carregamento;
* respostas vazias;
* dados inexistentes.

---

# 28. Integração final com Alane e Samara

Até **25/10**, os mocks principais deverão ter sido substituídos pelas chamadas reais da API.

Fluxo esperado:

```text
React
  ↓
Service do Frontend
  ↓
Django REST API
  ↓
Controller
  ↓
Service
  ↓
Repository
  ↓
Firestore
```

A equipe deverá evitar deixar a integração real para o dia 26.

---

# 29. 26/10 — Entrega final

## Data

**26/10/2026**

O dia 26 não deverá ser utilizado para desenvolvimento de novas funcionalidades.

Deverá ser utilizado para:

* validação final;
* correção de bugs críticos;
* testes;
* revisão do README;
* revisão do contrato da API;
* organização do Git;
* conferência do frontend;
* conferência do backend;
* demonstração do sistema.

---

# 30. Entregáveis finais

Até **26/10/2026**, o projeto deverá possuir:

### Backend

```text
Django funcionando
Firebase funcionando
Firestore funcionando
Firebase Authentication integrado
Controllers
Services
Repositories
Models
Schemas
Middleware
Tratamento de erros
Testes
API REST
Documentação
```

### Frontend

```text
React + Vite
Login
Dashboard
Perfil
Desafios
Pontuação
Ranking
Indicadores
Integração com API
```

### Integração

```text
Frontend
   ↓
API
   ↓
Backend
   ↓
Firestore
```

funcionando de ponta a ponta.

---

# 31. Definition of Done

Uma tarefa somente será considerada concluída quando:

* código implementado;
* código testado;
* integração realizada quando aplicável;
* resposta da API validada;
* tratamento de erro implementado;
* documentação atualizada;
* código versionado no Git;
* revisão realizada.

Não considerar:

```text
"o código está pronto na minha máquina"
```

como tarefa concluída.

Considerar:

```text
Implementado
+
Testado
+
Integrado
+
Versionado
+
Documentado
```

---

# 32. Git e branches

Recomendação:

```text
main
│
├── develop
│
├── feature/users
├── feature/challenges
├── feature/points
├── feature/ranking
└── feature/dashboard
```

Cada integrante deverá trabalhar em sua própria branch.

Exemplo:

```bash
git checkout -b feature/ranking
```

Commits devem ser objetivos:

```text
feat: cria endpoint de ranking
feat: implementa repository de usuários
fix: corrige cálculo de pontos
test: adiciona testes do ranking
docs: atualiza contrato da API
```

---

# 33. Regra principal de integração

O projeto será desenvolvido em paralelo.

Portanto:

```text
Carlos + Jonathan
        ↓
Contrato da API
        ↓
Alane + Samara
        ↓
Frontend utilizando Mock
        ↓
Backend implementa endpoint
        ↓
Integração
        ↓
Teste
```

Isso evita que o frontend fique parado esperando o backend.

---

# 34. Comunicação entre as equipes

Antes de implementar uma funcionalidade que será consumida pelo frontend, Carlos e Jonathan deverão informar:

```text
Endpoint
Método HTTP
Parâmetros
Headers
Autenticação
Body
Resposta de sucesso
Resposta de erro
Status HTTP
```

Exemplo:

```text
Endpoint:
GET /api/ranking/

Autenticação:
Bearer Token

Resposta:
{
    "success": true,
    "data": [...]
}
```

Alane e Samara deverão desenvolver utilizando esse contrato.

Se o contrato mudar, a alteração deverá ser comunicada antes de modificar o frontend.

---

# 35. Regra para mudanças na API

Evitar alterar um endpoint já utilizado pelo frontend sem comunicar a equipe.

Caso seja necessário alterar:

```text
1. Comunicar alteração
2. Atualizar contrato
3. Atualizar backend
4. Atualizar frontend
5. Testar integração
```

---

# 36. Resultado esperado em 26/10

Ao final do projeto, o sistema deverá apresentar:

```text
              GPADS
                │
        Dashboard Gamificada
                │
        ┌───────┴────────┐
        │                │
      Usuário          Admin
        │                │
   ┌────┼────┐       ┌───┼────┐
   │    │    │       │   │    │
 Perfil Desafios Ranking  │ Dashboard
   │    │    │           │
   └────┼────┘        Gestão
        │
     Pontos
        │
      Nível
```

Com a arquitetura:

```text
React + Vite
      ↓
Django REST API
      ↓
Services
      ↓
Repositories
      ↓
Firebase Firestore
```

e com o frontend e backend integrados até **26/10/2026**.

---

# 37. Resumo das responsabilidades

| Pessoa                | Responsabilidade principal                                   |
| --------------------- | ------------------------------------------------------------ |
| **Carlos**            | Controllers, Services, regras de negócio, autenticação e API |
| **Jonathan**          | Models, Schemas, Repositories e Firestore                    |
| **Alane**             | Frontend, telas, componentes e integração visual             |
| **Samara**            | Frontend, componentes, serviços e integração com API         |
| **Carlos + Jonathan** | Contrato da API e integração backend/frontend                |
| **Todos**             | Testes, revisão, integração e entrega                        |

---

# 38. Resumo do cronograma

| Período           | Sprint   | Objetivo                                                 |
| ----------------- | -------- | -------------------------------------------------------- |
| **05/10 → 11/10** | Sprint 1 | Fundação, Firebase, arquitetura e contrato da API        |
| **12/10 → 18/10** | Sprint 2 | Usuários, desafios, pontos, ranking e integração inicial |
| **19/10 → 25/10** | Sprint 3 | Dashboard, integração completa, testes e estabilização   |
| **26/10**         | Entrega  | Validação final e apresentação                           |

---

# 39. Prioridade do projeto

Como o prazo é curto, a prioridade deve ser:

```text
1. Autenticação
2. Usuários
3. Desafios
4. Pontuação
5. Ranking
6. Dashboard
7. Integração
8. Testes
9. Melhorias
```

Funcionalidades que não forem essenciais para a demonstração final não devem comprometer as funcionalidades principais.

---

# 40. Regra final para Carlos e Jonathan

O objetivo não é simplesmente "fazer o backend".

O objetivo é entregar uma **API funcional, previsível e documentada**, que Alane e Samara consigam consumir sem precisar conhecer a implementação interna do Django ou do Firestore.

A responsabilidade de vocês pode ser resumida assim:

```text
Jonathan
        ↓
"Garantir que os dados sejam armazenados
e recuperados corretamente."

Carlos
        ↓
"Garantir que as regras de negócio
e a API funcionem corretamente."

Alane + Samara
        ↓
"Garantir que o usuário consiga
utilizar essas funcionalidades no frontend."

Todos
        ↓
"Garantir que tudo funcione integrado
até 26/10/2026."
```

**Prazo final: 26/10/2026.**
