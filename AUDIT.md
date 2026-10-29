# Diagnóstico e decisões

Auditoria dos arquivos backend.zip, GpadsTech.md.txt e README.md anterior em 19/10/2026.

| Componente encontrado | Classificação inicial | Ação |
|---|---|---|
| manage.py, WSGI/ASGI, settings Django/DRF/CORS | Implementado, configuração básica | Preservado; adicionado DRF auth, erros, hosts configuráveis e limite de corpo. |
| GET /api/health/ | Implementado | Contrato literal preservado e testado por HTTP real local. |
| FirebaseConfig | Parcial | Inicialização funcional dependente de credencial; revisada para inicialização lazy e concorrência. Não validada com credencial real. |
| Controllers e Services de negócio | Apenas comentários | Implementados na mesma organização. |
| Models, Schemas, interfaces e Firebase repositories | Apenas comentários | Entidades, serializers, Protocols e adapters implementados. |
| Autenticação | Apenas comentário | Implementação DRF com verificador SDK e perfil Firestore. |
| Entregas/avaliações/pontos/ranking/dashboard | Ausentes como comportamento executável | Fluxo integrado implementado. |
| GitHub | Ausente | Client, mapper, serviço, permissões e recuperação adicionados. |
| user.controller.py | Nome incompatível com imports convencionais | Renomeado para user_controller.py. Não havia lógica a preservar. |
| app/main.py | Comentário desatualizado sobre FastAPI | Alias de aplicação WSGI Django. |
| Testes Firebase | Testes com conexão real; um escrevia system/connection_test | Substituídos por suíte offline e teste emulador opt-in restrito a loopback. Nenhum teste original foi executado. |
| README anterior | Incompatível com regras atuais de pontuação/Report | Atualizado; eliminada concessão automática por completar desafio. |

Não havia implementação funcional de endpoints de negócio a migrar, nem fixtures de dados oficiais. Nenhum esquema/credencial real foi consultado no Firestore.

## Decisões incrementais

1. Células representadas por cellId no estudante/atividade/entrega e ledCellIds no avaliador. Não foi criada uma coleção de células sem necessidade. Valores administrados fora da API pública.
2. role admin continua autorizando administração de desafios, mas não substitui vínculo de liderança para avaliar. Avaliador não pode avaliar sua própria entrega.
3. Avaliação e pontos são atômicos pelo UnitOfWork. A composição instancia repositories específicos; callbacks recebem interfaces, não o cliente Firestore.
4. Ledger points usa reportId como chave; total/ranking são derivados, sem coleção ranking. Os antigos arquivos ranking_repository e firebase_ranking_repository eram comentários e foram removidos por não haver persistência de ranking separada.
5. Exceções vazias anteriores foram consolidadas em application_exceptions.py. O antigo schema points era comentário; os registros Points são construídos pelo serviço a partir do model e validados pelo serializer de avaliação. Não existe endpoint de escrita de pontos direto.
6. Nível preservado; fórmula não definida pelas fontes. progress é indicador documentado de atividades avaliadas.
7. Correção usa /resubmit/; publicação recuperável usa /publish/. Não foram alterados endpoints funcionais anteriores.
8. A publicação adiciona UID e reportId abaixo do prefixo escolhido, usa report.md e code.txt, sem interpretar o código. Repositório deve existir e permitir escrita na branch padrão.
9. Schemas rejeitam propriedades desconhecidas. O exemplo conceitual files[] foi resolvido a favor do contrato report/code do pedido; anexos binários não foram implementados.
10. Não foi criada regra de impedimento de múltiplas entregas por atividade nem de prazo quinzenal: faltam critérios operacionais documentados. A deduplicação é por entrega finalizada.

## Segurança do pacote

Credenciais e .env do ZIP de origem não foram reproduzidos, usados nos testes ou incluídos no resultado. O pacote final não contém .git, ambientes virtuais, contas de serviço, caches ou bytecode. Como credenciais foram anexadas no arquivo de origem, cabe ao responsável revogar/substituir aquelas credenciais antes de uso em produção; nenhuma rotação foi executada aqui.
