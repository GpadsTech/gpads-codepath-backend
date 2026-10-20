# Validação executada

Ambiente: Python 3.12.14, Django 5.2.18, DRF 3.18.3, Firebase Admin 7.7.0, pytest 9.1.1, pytest-django 4.14.0.

- `python manage.py check`: **System check identified no issues (0 silenced)**.
- `python -m pytest -v` na pasta backend: **43 passed, 1 skipped**. Saída detalhada em test-results.txt.
- `python -m ruff check app tests`: **All checks passed**; formatter aplicado.
- Servidor `python manage.py runserver 127.0.0.1:8765 --noreload`: iniciado em subprocesso e encerrado após verificação; GET /api/health/ retornou HTTP 200 e o JSON original.

A primeira execução da suíte a partir da pasta externa não encontrou as configurações Django; executar dentro de backend resolveu a coleta. Na primeira execução válida, testes identificaram tratamento incorreto de campos desconhecidos e uma referência obsoleta no fake de teste após rollback. Ambos foram corrigidos antes do resultado final.

Cobertura comportamental: autenticação simulada válida/inválida/ausente; delegação ao SDK com check_revoked; edição de perfil; CRUD/desativação de desafios; envio/visibilidade; devolução/reenvio/histórico; aprovação 0/85/100; rejeição de tipos/valores inválidos; impedimento de reavaliação; avaliações concorrentes; autoavaliação; mudança de liderança; allowlist/prefixo/traversal; falha/rollback de persistência; GitHub HTTP/network/conflict; retry sem pontos duplicados; recuperação parcial e por checkpoint; leases expirados e publicação concorrente; ranking/empates/period; dashboard; tamanho máximo; resposta HTTP sem erro interno bruto.

## O que não foi validado

- Teste de emulador foi ignorado porque não foi solicitado/configurado um emulador local.
- Não houve login Firebase real, verificação criptográfica com token real nem escrita/leitura real no Firestore.
- Concorrência foi exercitada no UnitOfWork fake com lock/rollback; o adapter Firestore foi testado por mocks. Confirmar transações e contenção em emulador/staging é pendência de homologação.
- GitHub foi testado com transporte simulado: nenhum repositório recebeu commits. Ainda é necessário validar token, branch protections, IAM, quotas e permissões do destino real.
- Nenhum frontend executável foi fornecido: contrato e exemplo foram entregues, mas integração visual não foi executada.
- Não foram feitos testes de carga; consultas integrais de coleções são limite conhecido do MVP.

## Homologação necessária antes de 26/10

Em ambiente de teste separado, provisionar dois alunos de células diferentes e um líder; autenticar no React; executar envio, devolução, reenvio e avaliação; confirmar isolamento entre células; conferir um único points/{reportId}; repetir /publish/ e conferir ausência de novo ponto/commit quando o conteúdo já existe; simular falha de permissão GitHub; conferir dashboard e ranking. Usar somente dados de teste. Não há autorização implícita neste pacote para executar testes contra produção.
