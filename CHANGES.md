Change Logs
Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

**[v1.0.0] - 2025-10-04:**
Alteração do projeto para suportar build via `Docker`, utilizando o task para gerenciar rotinas e aplicar boas práticas de desenvolvimento conforme as PEPs. Também foram instaladas as bibliotecas necessárias, como `Flask` para criação da API RESTful, SQLAlchemy para ORM e orquestração de dados, Alembic para migrações de banco, `Poetry` para gerenciamento de dependências e Docker para administração das imagens do `PostgreSQL`.

**[v1.0.0] - 2025-10-05:**
Foram incluídas novas rotas no sistema para owner e company, seguindo o padrão estabelecido. Um proprietário pode possuir múltiplas companhias, cada uma identificada pelo seu próprio slug, definido conforme o domínio registrado no sistema, além de suas respectivas regras de unicidade.

**[v1.0.0] - 2025-11-12:**
Foram corrigidas as chaves estrangeiras de acordo com a estrutura exigida pela tabela de usuários. Também foi ajustado corretamente o controle do isort e do black, garantindo importações ordenadas e quebras de linha padronizadas. Além disso, foi adicionado o módulo de colaboradores associados à empresa.

**[v1.0.0] - 2025-11-14:**
Foi adicionado o módulo completo de agenda e de produtos — utilizei o termo produto porque representa os serviços prestados pelos barbeiros. Além disso, implementei também o bloqueio de agenda, os filtros e uma reorganização dos linters, incluindo a reconfiguração do `pyproject.toml`.