# GPADS CodePath Backend

API Django REST com Firebase Authentication/Firestore, entregas quinzenais, avaliação, pontos, publicação GitHub, seleção de avatar e geração de rascunhos com Gemini.

Consulte [DEPLOY.md](DEPLOY.md) para configuração completa do Render, Firebase, permissões de líderes e integração com o frontend.

## Desenvolvimento

Use Python 3.12+, instale requirements.txt e configure .env a partir de .env.example. Nunca publique .env ou credentials/.

- Executar: python manage.py runserver
- Verificar: python manage.py check
- Testes sem chamadas externas: pytest -q
- Saúde: GET /api/health/
- Cadastro exclusivo de líderes: GET/POST /api/students/
- IA: GET/POST /api/ai/report/

Documentos users usam o UID do Firebase Authentication como ID. Não há cadastro público de líderes ou promoção de papéis pelo frontend.
