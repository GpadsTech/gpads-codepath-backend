# 🎮 GPADS CodePath — Backend

Backend oficial do **GPADS CodePath**.

Este projeto fornece a API responsável por autenticação, usuários, desafios, atividades, pontuação, níveis, ranking e indicadores utilizados pelo frontend da plataforma.

O backend foi desenvolvido em **Python + Django + Django REST Framework**, utilizando **Firebase Firestore** como banco de dados.

---

# 1. 🎯 O que é o sistema?

O GPADS CodePath é uma plataforma que transforma atividades e participação dos usuários em uma experiência gamificada.

A ideia é permitir que o usuário:

* acompanhe suas atividades;
* conclua desafios;
* acumule pontos;
* evolua de nível;
* acompanhe seu desempenho;
* visualize seu posicionamento no ranking;
* acompanhe indicadores;
* consulte seu histórico.

Administradores terão recursos adicionais para:

* cadastrar e gerenciar desafios;
* acompanhar usuários;
* acompanhar pontuação;
* visualizar indicadores;
* consultar relatórios;
* administrar conteúdos da plataforma.

---

# 2. 🏗️ Arquitetura geral

O sistema será dividido em três partes principais:

```text
┌─────────────────────────────────────┐
│             FRONTEND                │
│           React + Vite              │
└──────────────────┬──────────────────┘
                   │
                   │ HTTP / REST / JSON
                   ▼
┌─────────────────────────────────────┐
│              BACKEND                │
│        Django + DRF + Python        │
│                                     │
│ Controller                          │
│      ↓                              │
│ Service                             │
│      ↓                              │
│ Repository Interface                │
│      ↓                              │
│ Firebase Repository                 │
└──────────────────┬──────────────────┘
                   │
                   ▼
┌─────────────────────────────────────┐
│           FIREBASE                  │
│                                     │
│ Firebase Authentication             │
│ Firestore                           │
└─────────────────────────────────────┘
```

O frontend **não deve acessar diretamente o Firestore para executar as regras de negócio da aplicação**.

A comunicação principal será:

```text
Frontend
   ↓
API Django
   ↓
Services
   ↓
Repositories
   ↓
Firestore
```

---

# 3. 🧠 Princípio principal da arquitetura

Cada camada possui uma responsabilidade.

```text
Controller
→ recebe requisições e devolve respostas.

Service
→ executa as regras de negócio.

Repository Interface
→ define o contrato de persistência.

Firebase Repository
→ executa a persistência no Firestore.

Model
→ representa entidades do domínio.

Schema
→ define o formato dos dados de entrada e saída.

Middleware
→ executa validações/interceptações da requisição.

Exception
→ representa erros específicos do domínio.
```

Regra fundamental:

> **Não colocar toda a lógica em uma única classe.**

---

# 4. 📁 Estrutura do projeto

```text
backend/
│
├── app/
│   │
│   ├── main.py
│   │
│   ├── config/
│   │   ├── settings.py
│   │   ├── firebase.py
│   │   ├── urls.py
│   │   ├── asgi.py
│   │   └── wsgi.py
│   │
│   ├── controllers/
│   │   ├── auth_controller.py
│   │   ├── user_controller.py
│   │   ├── challenge_controller.py
│   │   ├── points_controller.py
│   │   ├── ranking_controller.py
│   │   └── report_controller.py
│   │
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── user_service.py
│   │   ├── challenge_service.py
│   │   ├── points_service.py
│   │   ├── ranking_service.py
│   │   └── report_service.py
│   │
│   ├── repositories/
│   │   ├── interfaces/
│   │   │   ├── user_repository.py
│   │   │   ├── challenge_repository.py
│   │   │   └── points_repository.py
│   │   │
│   │   └── firebase/
│   │       ├── firebase_user_repository.py
│   │       ├── firebase_challenge_repository.py
│   │       └── firebase_points_repository.py
│   │
│   ├── models/
│   │   ├── user.py
│   │   ├── challenge.py
│   │   ├── points.py
│   │   └── report.py
│   │
│   ├── schemas/
│   │   ├── user_schema.py
│   │   ├── challenge_schema.py
│   │   ├── points_schema.py
│   │   └── report_schema.py
│   │
│   ├── middleware/
│   │   └── auth_middleware.py
│   │
│   └── exceptions/
│       ├── user_exceptions.py
│       ├── challenge_exceptions.py
│       └── auth_exceptions.py
│
├── credentials/
│   └── firebase-service-account.json
│
├── tests/
│
├── manage.py
├── requirements.txt
├── pytest.ini
├── .env
├── .env.example
└── .gitignore
```

---

# 5. 🔥 Firebase

O banco principal da aplicação é o:

**Firebase Firestore**

As credenciais são carregadas através do `.env`.

```env
FIREBASE_CREDENTIALS_PATH=credentials/firebase-service-account.json
```

O arquivo de credenciais nunca deve ser enviado para o Git.

---

# 6. 🗃️ Estrutura inicial do Firestore

A estrutura inicial será:

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

---

## 6.1 `users`

Representa os usuários.

```text
users/{uid}
```

Exemplo:

```json
{
  "name": "Nome do usuário",
  "email": "usuario@email.com",
  "role": "user",
  "points": 0,
  "level": 1,
  "createdAt": "timestamp"
}
```

---

## 6.2 `challenges`

Representa os desafios.

```text
challenges/{challengeId}
```

Exemplo:

```json
{
  "title": "Nome do desafio",
  "description": "Descrição",
  "points": 100,
  "difficulty": "medium",
  "status": "active",
  "createdAt": "timestamp"
}
```

---

## 6.3 `points`

Representa o histórico de pontuação.

```text
points/{pointId}
```

Exemplo:

```json
{
  "userId": "uid",
  "challengeId": "challengeId",
  "points": 100,
  "reason": "Desafio concluído",
  "createdAt": "timestamp"
}
```

---

## 6.4 `reports`

Representará informações utilizadas pelos indicadores e relatórios.

A estrutura definitiva será definida conforme os indicadores forem implementados.

---

# 7. 👥 Usuários e papéis

O sistema terá, inicialmente, dois papéis:

```text
user
admin
```

### User

Pode:

* visualizar seu perfil;
* visualizar desafios disponíveis;
* concluir atividades;
* ganhar pontos;
* acompanhar seu nível;
* visualizar ranking;
* visualizar seus indicadores.

### Admin

Pode, conforme as permissões definidas:

* gerenciar desafios;
* consultar usuários;
* acompanhar pontuação;
* consultar indicadores;
* consultar relatórios.

As permissões devem ser verificadas no backend.

**Nunca confiar somente no frontend para impedir uma operação administrativa.**

---

# 8. 🔐 Autenticação

A autenticação será baseada no:

**Firebase Authentication**

O frontend fará o login e receberá um token.

Esse token será enviado para a API:

```http
Authorization: Bearer <TOKEN>
```

O backend deverá:

1. receber o token;
2. validar o token;
3. identificar o usuário;
4. verificar seu papel;
5. permitir ou negar a operação.

Fluxo:

```text
Frontend
   │
   │ Login
   ▼
Firebase Authentication
   │
   │ ID Token
   ▼
Frontend
   │
   │ Authorization: Bearer TOKEN
   ▼
Django
   │
   ▼
Auth Middleware
   │
   ├── válido → Controller
   │
   └── inválido → 401
```

---

# 9. 🧱 Responsabilidade de cada classe

## 9.1 `FirebaseConfig`

Arquivo:

```text
app/config/firebase.py
```

Responsabilidade:

* carregar credenciais;
* inicializar Firebase Admin SDK;
* fornecer acesso ao Firestore.

Não deve:

* calcular pontos;
* validar desafios;
* manipular usuários;
* implementar regras de negócio.

---

# 10. 🎮 Controllers

Os Controllers são a porta de entrada da API.

Eles recebem:

```text
HTTP Request
```

e devolvem:

```text
HTTP Response
```

---

## `AuthController`

Responsável por endpoints relacionados à autenticação e informações do usuário autenticado.

Não deve implementar a validação do Firebase diretamente.

Essa responsabilidade fica no middleware/service.

---

## `UserController`

Responsável por:

* buscar usuário;
* atualizar perfil;
* consultar informações do usuário;
* retornar dados necessários para o dashboard.

---

## `ChallengeController`

Responsável por:

* listar desafios;
* consultar desafio;
* criar desafio;
* atualizar desafio;
* desativar desafio;
* concluir desafio.

---

## `PointsController`

Responsável por:

* consultar pontuação;
* consultar histórico;
* retornar informações de pontos.

A regra de atribuição dos pontos fica no Service.

---

## `RankingController`

Responsável por:

* retornar ranking;
* consultar posição do usuário;
* consultar usuários próximos na classificação.

---

## `ReportController`

Responsável por:

* retornar indicadores;
* consultar métricas;
* retornar dados necessários aos gráficos.

---

# 11. 🧠 Services

Os Services possuem as regras de negócio.

---

## `AuthService`

Responsável por:

* validar informações do usuário;
* consultar perfil;
* verificar papel;
* aplicar regras relacionadas à autenticação.

---

## `UserService`

Responsável por:

* criar perfil;
* consultar perfil;
* atualizar perfil;
* validar operações permitidas.

---

## `ChallengeService`

Responsável pelas regras dos desafios.

Exemplos:

```text
Usuário pode concluir?
Desafio está ativo?
Usuário já concluiu?
Quantos pontos recebe?
```

---

## `PointsService`

Responsável por:

* registrar pontos;
* validar pontuação;
* atualizar saldo;
* consultar histórico;
* calcular evolução.

---

## `RankingService`

Responsável por:

* calcular classificação;
* ordenar usuários;
* determinar posição;
* tratar empates.

---

## `ReportService`

Responsável por:

* consolidar dados;
* calcular indicadores;
* preparar informações para gráficos;
* gerar métricas para o dashboard.

---

# 12. 🗄️ Repositories

Repositories são responsáveis exclusivamente pela persistência.

Exemplo:

```text
UserService
     │
     ▼
IUserRepository
     │
     ▼
FirebaseUserRepository
     │
     ▼
Firestore
```

O Service não deve conhecer os detalhes do Firestore.

---

# 13. 📜 Interfaces

As interfaces definem o contrato dos repositories.

Exemplo:

```python
class IUserRepository:

    def find_by_id(self, user_id):
        pass

    def create(self, user):
        pass

    def update(self, user_id, data):
        pass
```

A implementação Firebase:

```python
class FirebaseUserRepository(IUserRepository):

    def find_by_id(self, user_id):
        ...

    def create(self, user):
        ...

    def update(self, user_id, data):
        ...
```

Isso permite testar Services sem depender diretamente do Firebase.

---

# 14. 📦 Models

Models representam as entidades do domínio.

Principais:

```text
User
Challenge
Points
Report
```

Exemplo:

```python
class User:
    def __init__(
        self,
        id,
        name,
        email,
        role,
        points,
        level
    ):
        self.id = id
        self.name = name
        self.email = email
        self.role = role
        self.points = points
        self.level = level
```

O Model não deve ser responsável por acessar Firestore.

---

# 15. 📥📤 Schemas

Schemas definem os contratos dos dados.

Exemplo:

```json
{
  "name": "Nathália",
  "email": "nathalia@email.com"
}
```

O Schema determina:

* campos obrigatórios;
* tipos;
* estrutura;
* validações básicas.

---

# 16. 🔌 CONTRATO DA API

Esta é uma das partes mais importantes para a integração entre backend e frontend.

O frontend e o backend devem concordar antecipadamente sobre:

* URL;
* método HTTP;
* autenticação;
* parâmetros;
* corpo da requisição;
* resposta;
* códigos HTTP;
* mensagens de erro.

---

# 17. 📋 Padrão de resposta

As respostas da API devem seguir um padrão consistente.

### Sucesso

```json
{
  "success": true,
  "data": {}
}
```

### Erro

```json
{
  "success": false,
  "error": {
    "code": "USER_NOT_FOUND",
    "message": "Usuário não encontrado."
  }
}
```

O frontend não deve precisar interpretar dezenas de formatos diferentes de resposta.

---

# 18. 👤 API — Usuários

## Buscar usuário

```http
GET /api/users/{userId}/
```

Resposta:

```json
{
  "success": true,
  "data": {
    "id": "abc123",
    "name": "Nathália",
    "email": "nathalia@email.com",
    "role": "user",
    "points": 850,
    "level": 3
  }
}
```

---

## Atualizar usuário

```http
PATCH /api/users/{userId}/
```

Request:

```json
{
  "name": "Novo nome"
}
```

Resposta:

```json
{
  "success": true,
  "data": {
    "id": "abc123",
    "name": "Novo nome"
  }
}
```

---

# 19. 🎯 API — Desafios

## Listar desafios

```http
GET /api/challenges/
```

Resposta:

```json
{
  "success": true,
  "data": [
    {
      "id": "challenge01",
      "title": "Completar atividade",
      "description": "Complete a atividade proposta.",
      "points": 100,
      "difficulty": "medium",
      "status": "active"
    }
  ]
}
```

---

## Buscar desafio

```http
GET /api/challenges/{challengeId}/
```

---

## Criar desafio

Somente admin.

```http
POST /api/challenges/
```

Request:

```json
{
  "title": "Novo desafio",
  "description": "Descrição do desafio",
  "points": 100,
  "difficulty": "medium"
}
```

---

## Atualizar desafio

Somente admin.

```http
PATCH /api/challenges/{challengeId}/
```

---

## Desativar desafio

Somente admin.

```http
DELETE /api/challenges/{challengeId}/
```

A exclusão física deve ser evitada quando houver necessidade de preservar histórico.

Preferir desativação:

```json
{
  "status": "inactive"
}
```

---

# 20. ⭐ API — Pontuação

## Consultar pontuação

```http
GET /api/users/{userId}/points/
```

Resposta:

```json
{
  "success": true,
  "data": {
    "total": 850,
    "level": 3
  }
}
```

---

## Histórico de pontos

```http
GET /api/users/{userId}/points/history/
```

Resposta:

```json
{
  "success": true,
  "data": [
    {
      "id": "point01",
      "challengeId": "challenge01",
      "points": 100,
      "reason": "Desafio concluído",
      "createdAt": "2026-10-04T20:00:00Z"
    }
  ]
}
```

---

# 21. 🏆 API — Ranking

## Ranking geral

```http
GET /api/ranking/
```

Resposta:

```json
{
  "success": true,
  "data": [
    {
      "position": 1,
      "userId": "user01",
      "name": "Usuário 1",
      "points": 1500,
      "level": 5
    },
    {
      "position": 2,
      "userId": "user02",
      "name": "Usuário 2",
      "points": 1200,
      "level": 4
    }
  ]
}
```

---

## Posição do usuário

```http
GET /api/ranking/me/
```

Resposta:

```json
{
  "success": true,
  "data": {
    "position": 8,
    "points": 850,
    "level": 3
  }
}
```

---

# 22. 📊 API — Dashboard e relatórios

O frontend precisará de dados para alimentar:

* cards;
* gráficos;
* ranking;
* progresso;
* indicadores;
* histórico.

Exemplo:

```http
GET /api/dashboard/
```

Resposta:

```json
{
  "success": true,
  "data": {
    "points": 850,
    "level": 3,
    "completedChallenges": 12,
    "rankingPosition": 8,
    "progress": 72
  }
}
```

A ideia é evitar que o frontend precise fazer várias requisições para montar uma única tela quando isso puder ser resolvido adequadamente no backend.

---

# 23. 📡 Contrato API × Frontend

O frontend deve consumir apenas os contratos definidos.

Exemplo:

```text
Frontend
   │
   │ GET /api/dashboard/
   ▼
Backend
   │
   ▼
DashboardService
   │
   ▼
Repositories
   │
   ▼
Firestore
```

O frontend não precisa saber:

```text
como o Firestore funciona
como a collection está estruturada
como os dados são consultados
como os pontos são calculados
```

Ele só precisa conhecer:

```text
endpoint
request
response
```

---

# 24. 🔴 Códigos HTTP

Usar códigos HTTP de forma consistente.

```text
200 OK
→ operação realizada.

201 CREATED
→ recurso criado.

204 NO CONTENT
→ operação realizada sem conteúdo de retorno.

400 BAD REQUEST
→ dados enviados são inválidos.

401 UNAUTHORIZED
→ usuário não autenticado.

403 FORBIDDEN
→ usuário autenticado, mas sem permissão.

404 NOT FOUND
→ recurso não encontrado.

409 CONFLICT
→ conflito de estado/dados.

500 INTERNAL SERVER ERROR
→ erro inesperado no backend.
```

---

# 25. ⚠️ Contrato de erros

Exemplo:

```json
{
  "success": false,
  "error": {
    "code": "CHALLENGE_ALREADY_COMPLETED",
    "message": "Este desafio já foi concluído pelo usuário."
  }
}
```

O frontend poderá utilizar o `code` para tomar decisões.

Não depender apenas da mensagem textual.

---

# 26. 🔄 Exemplo completo

Usuário conclui desafio.

### Frontend

```http
POST /api/challenges/challenge01/complete/
Authorization: Bearer TOKEN
```

### Backend

```text
AuthMiddleware
       ↓
ChallengeController
       ↓
ChallengeService
       ↓
ChallengeRepository
       ↓
Firestore
```

Depois:

```text
ChallengeService
       ↓
PointsService
       ↓
PointsRepository
       ↓
Firestore
```

Resposta:

```json
{
  "success": true,
  "data": {
    "challengeId": "challenge01",
    "completed": true,
    "pointsEarned": 100,
    "totalPoints": 950,
    "level": 3,
    "levelUp": false
  }
}
```

O frontend simplesmente utiliza esses dados para atualizar a interface.

---

# 27. 👥 Divisão de responsabilidades

## 👨‍💻 Carlos — Backend / Regras e API

Carlos ficará principalmente responsável pela camada de aplicação.

### Responsabilidades

* Controllers;
* Services;
* regras de negócio;
* autenticação;
* autorização;
* integração dos endpoints;
* tratamento das respostas;
* integração final com o frontend;
* testes dos Services.

### Principais arquivos

```text
controllers/
services/
middleware/
exceptions/
```

Carlos deverá trabalhar em conjunto com Jonathan quando uma funcionalidade depender do Repository.

---

# 28. 👨‍💻 Jonathan — Backend / Dados e Firebase

Jonathan ficará principalmente responsável pela camada de persistência.

### Responsabilidades

* Models;
* Schemas;
* Repository Interfaces;
* Firebase Repositories;
* Firestore;
* estrutura das collections;
* consultas;
* operações CRUD;
* testes dos Repositories;
* integração Firebase.

### Principais arquivos

```text
models/
schemas/
repositories/
config/firebase.py
```

---

# 29. 🤝 Trabalho conjunto

Algumas partes não pertencem exclusivamente a uma pessoa.

Carlos e Jonathan devem trabalhar juntos em:

* definição do contrato da API;
* definição dos documentos Firestore;
* autenticação;
* testes de integração;
* revisão de código;
* integração com frontend;
* correção de bugs;
* documentação.

A regra é:

```text
Jonathan
→ garante que os dados possam ser armazenados/consultados.

Carlos
→ garante que as regras de negócio utilizem esses dados corretamente.
```

---

# 30. 🗓️ Sprints

Cada Sprint possui duração de **1 semana**.

O objetivo é terminar cada Sprint com uma entrega funcional.

---

# 🟦 SPRINT 1 — Infraestrutura e contrato

### Objetivo

Deixar a base do backend pronta e estabelecer o contrato com o frontend.

### Carlos

* revisar Controllers;
* configurar estrutura inicial da API;
* criar health check;
* preparar estrutura de respostas;
* iniciar documentação dos endpoints.

### Jonathan

* configurar Firebase;
* validar Firestore;
* criar Repository Interfaces;
* definir estrutura inicial das collections;
* validar conexão de leitura/escrita.

### Ambos

* validar arquitetura;
* definir entidades;
* definir contrato inicial da API;
* configurar testes.

### Entrega

```text
Django funcionando
+
Firebase funcionando
+
Firestore funcionando
+
API Health Check
+
Contrato inicial definido
```

---

# 🟩 SPRINT 2 — Autenticação e usuários

### Objetivo

Implementar usuários e autenticação.

### Carlos

* AuthController;
* AuthService;
* middleware de autenticação;
* autorização por role;
* endpoints de usuário.

### Jonathan

* User Model;
* User Schema;
* IUserRepository;
* FirebaseUserRepository;
* collection `users`.

### Ambos

* testes;
* integração;
* validação do contrato.

### Entrega

```text
Login
↓
Token
↓
Django
↓
Usuário autenticado
↓
Perfil
```

---

# 🟨 SPRINT 3 — Desafios

### Objetivo

Implementar o sistema de desafios.

### Carlos

* ChallengeController;
* ChallengeService;
* regras de conclusão;
* permissões administrativas.

### Jonathan

* Challenge Model;
* Challenge Schema;
* Challenge Repository;
* Firestore `challenges`.

### Ambos

* testes;
* documentação;
* integração com frontend.

### Entrega

```text
Listar desafios
Criar desafio
Editar desafio
Desativar desafio
Consultar desafio
```

---

# 🟧 SPRINT 4 — Pontuação e níveis

### Objetivo

Implementar o núcleo da gamificação.

### Carlos

* PointsService;
* regras de pontuação;
* regras de nível;
* conclusão de desafios;
* integração entre desafio e pontos.

### Jonathan

* Points Model;
* Points Schema;
* Points Repository;
* histórico de pontos.

### Ambos

* testes;
* validação de cálculos;
* integração com frontend.

### Entrega

```text
Desafio concluído
       ↓
Pontos recebidos
       ↓
Total atualizado
       ↓
Nível recalculado
```

---

# 🟥 SPRINT 5 — Ranking

### Objetivo

Implementar o ranking dos usuários.

### Carlos

* RankingService;
* regras de ordenação;
* posição;
* empates;
* RankingController.

### Jonathan

* consultas necessárias no Firestore;
* otimização das consultas;
* suporte à paginação, se necessário.

### Ambos

* testes;
* integração com frontend.

### Entrega

```text
Ranking geral
+
posição do usuário
+
pontuação
+
nível
```

---

# 🟪 SPRINT 6 — Dashboard e indicadores

### Objetivo

Fornecer os dados necessários para o dashboard.

### Carlos

* ReportService;
* DashboardService;
* endpoints de indicadores;
* agregação dos dados.

### Jonathan

* consultas Firestore;
* estrutura dos dados de relatório;
* otimização das consultas.

### Ambos

* contrato dos gráficos;
* testes;
* integração com frontend.

### Entrega

```text
Dashboard
├── Pontos
├── Nível
├── Desafios
├── Ranking
├── Progresso
└── Indicadores
```

---

# ⬛ SPRINT 7 — Integração e estabilização

### Objetivo

Integrar todas as partes.

### Carlos

* correção dos endpoints;
* tratamento de erros;
* validação de autenticação;
* integração final.

### Jonathan

* revisão do Firestore;
* correção de consultas;
* performance;
* consistência dos dados.

### Ambos

* testes de integração;
* correção de bugs;
* revisão de código;
* documentação;
* suporte ao frontend.

### Entrega

Backend integrado com frontend.

---

# 🏁 SPRINT 8 — Finalização

### Objetivo

Preparar o sistema para apresentação/entrega.

### Ambos

* testes finais;
* documentação;
* revisão de segurança;
* revisão das APIs;
* limpeza do código;
* correção de bugs;
* validação do ambiente de produção.

### Entrega

```text
Backend
+
Frontend
+
Firebase
+
Firestore
+
API
+
Testes
+
Documentação
```

---

# 31. ⏱️ Prazo de cada Sprint

Cada Sprint possui:

```text
Duração: 1 semana
```

Fluxo recomendado:

```text
SEGUNDA
Planejamento
    ↓
TERÇA–QUINTA
Desenvolvimento
    ↓
SEXTA
Integração + testes
    ↓
FIM DA SPRINT
Entrega
```

A Sprint só deve ser considerada concluída quando a funcionalidade estiver:

```text
Implementada
+
Testada
+
Integrada
+
Documentada
```

---

# 32. 🔀 Fluxo de desenvolvimento

Para cada tarefa:

```text
1. Criar branch
2. Implementar
3. Testar
4. Commit
5. Push
6. Pull Request
7. Code Review
8. Merge
```

Exemplo:

```bash
git checkout -b feature/challenges
```

Depois:

```bash
git add .
git commit -m "feat: implementa desafios"
git push origin feature/challenges
```

---

# 33. 📝 Padrão de commits

Utilizar Conventional Commits.

Exemplos:

```text
feat: adiciona endpoint de desafios
fix: corrige cálculo de pontos
test: adiciona testes de ranking
refactor: separa regra de pontuação
docs: atualiza contrato da API
chore: atualiza dependências
```

---

# 34. 🧪 Definition of Done

Uma tarefa só está concluída quando:

```text
[ ] Código implementado
[ ] Arquitetura respeitada
[ ] SOLID respeitado
[ ] Testes criados
[ ] Testes passando
[ ] Endpoint documentado
[ ] Contrato definido
[ ] Frontend consegue consumir
[ ] Erros tratados
[ ] Code review realizado
```

---

# 35. 🚨 Regras importantes para Carlos e Jonathan

### 1. Não acessar Firestore diretamente no Controller.

Errado:

```text
Controller
    ↓
Firestore
```

Correto:

```text
Controller
    ↓
Service
    ↓
Repository
    ↓
Firestore
```

---

### 2. Não colocar regra de negócio no Repository.

Repository salva e consulta.

Quem decide **o que deve acontecer** é o Service.

---

### 3. Não confiar no frontend para segurança.

Mesmo que o botão de administrador não apareça no frontend, o backend precisa verificar:

```text
usuário autenticado?
+
usuário possui permissão?
```

---

### 4. O contrato da API deve ser combinado antes da integração.

Não alterar silenciosamente:

```text
endpoint
campo
tipo
status HTTP
estrutura JSON
```

porque isso pode quebrar o frontend.

---

### 5. Toda mudança de contrato deve ser comunicada.

Exemplo:

Antes:

```json
{
  "points": 100
}
```

Depois:

```json
{
  "score": 100
}
```

Essa mudança quebra o frontend.

Portanto, deve ser discutida antes.

---

# 36. 🚀 Como executar

## Backend

```bash
cd backend
```

Ativar ambiente:

```bash
venv\Scripts\activate
```

Instalar dependências:

```bash
pip install -r requirements.txt
```

Verificar Django:

```bash
python manage.py check
```

Executar migrations:

```bash
python manage.py migrate
```

Executar testes:

```bash
pytest -v
```

Executar servidor:

```bash
python manage.py runserver
```

API:

```text
http://127.0.0.1:8000/
```

Health check:

```text
http://127.0.0.1:8000/api/health/
```

---

# 37. 🌐 Frontend

Em outro terminal:

```bash
cd frontend
npm install
npm run dev
```

Normalmente:

```text
http://localhost:5173/
```

---

# 38. 🔗 Integração

Durante o desenvolvimento:

```text
                 ┌──────────────┐
                 │   FRONTEND   │
                 │ React + Vite │
                 └──────┬───────┘
                        │
                     REST API
                        │
                        ▼
                 ┌──────────────┐
                 │    DJANGO    │
                 └──────┬───────┘
                        │
                 ┌──────▼───────┐
                 │ CONTROLLER   │
                 └──────┬───────┘
                        │
                 ┌──────▼───────┐
                 │   SERVICE    │
                 └──────┬───────┘
                        │
                 ┌──────▼───────┐
                 │  REPOSITORY  │
                 └──────┬───────┘
                        │
                 ┌──────▼───────┐
                 │  FIRESTORE   │
                 └──────────────┘
```

---

# 39. 🎯 Objetivo final

O objetivo não é apenas fazer endpoints funcionarem.

O objetivo é construir um backend:

* organizado;
* testável;
* seguro;
* escalável;
* fácil de manter;
* desacoplado do frontend;
* preparado para evolução.

A principal regra do projeto é:

> **O frontend consome contratos. O backend implementa regras. O repository gerencia persistência. O Firestore armazena os dados.**

Se cada integrante respeitar essa divisão, Carlos e Jonathan poderão desenvolver simultaneamente sem ficarem bloqueados um pelo outro.

---

# 40. 📌 Resumo rápido para a equipe

```text
CARLOS
│
├── Controllers
├── Services
├── Auth
├── Middleware
├── Regras de negócio
└── Integração da API

JONATHAN
│
├── Models
├── Schemas
├── Repository Interfaces
├── Firebase Repositories
├── Firestore
└── Persistência

AMBOS
│
├── Contrato da API
├── Testes
├── Integração
├── Code Review
└── Documentação
```

E o fluxo que todos devem memorizar:

```text
FRONTEND
   ↓
CONTROLLER
   ↓
SERVICE
   ↓
REPOSITORY INTERFACE
   ↓
FIREBASE REPOSITORY
   ↓
FIRESTORE
```

Esse fluxo é a base arquitetural do backend do GPADS Dashboard Gamificada.
