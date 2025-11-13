Change Logs
Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

**[v1.0.0] - 2025-10-04:**
Alteração do projeto com buildagem docker, utilizando o `task`, para gerenciar pacotes de boas práticas de desenvolvimento de software de acordo com a pep, instalação das libs necessárias, tais como `flask` para criar api-restfull, `sqlalchemy` para orm e orquestração de dados, `alembic` para migração de banco de dados, `poetry` para gerenciamento de pacotes, `docker` para gerenciar imagens do `postgres`.

**[v1.0.0] - 2025-10-05:**
Incluindo novas rotas no sistema com `owner`, e `company`, de acordo com o padrão do sistema, um proprietário pode ter mais de uma companhia, e cada uma tem seu `slug`, de acordo com o dominio registrado do sistema. Fora suas regras de unicidade.

**[v1.0.0] - 2025-11-12:**
Ajustando corretamente as Fk de acordo com oque a tabela do usuário solicita, também foi ajustado corretamente o controle do `isort`, `.black`, com isso tendo a importação e a quebra de linha corretamente, adicionando o module do colaborador associado a empresa.