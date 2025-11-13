"""Set company_id not null"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text

# revision identifiers
revision = '6ca4ceee9809'
down_revision = '8f7df58863ed'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Preenche company_id nulos e define NOT NULL."""
    conn = op.get_bind()

    # 🔹 Busca qualquer empresa existente
    result = conn.execute(text("SELECT id FROM companies LIMIT 1;"))
    company_id = result.scalar()

    # 🔹 Se não existir, cria uma empresa padrão
    if not company_id:
        conn.execute(text("INSERT INTO companies (name) VALUES ('Empresa Padrão');"))
        result = conn.execute(text("SELECT id FROM companies LIMIT 1;"))
        company_id = result.scalar()

    # 🔹 Atualiza todos os usuários sem empresa
    conn.execute(
        text("UPDATE users SET company_id = :company_id WHERE company_id IS NULL;"),
        {"company_id": company_id}
    )

    # 🔹 Agora altera para NOT NULL
    op.alter_column(
        'users',
        'company_id',
        existing_type=sa.Integer(),
        nullable=False
    )


def downgrade() -> None:
    op.alter_column('users', 'company_id', nullable=True)
