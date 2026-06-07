"""initial schema (baseline no-op)

Revision ID: f6648415e873
Revises:
Create Date: 2026-06-07 11:30:41.838692

NOTA: Esta migration foi gerada via autogenerate em SQLite que JA tinha tabelas
criadas via Base.metadata.create_all(). Por isso o autogenerate so detectou
diferencas (NUMERIC->UUID) em vez de CREATE TABLE.

Para destravar o deploy, esta migration eh agora um BASELINE NO-OP:
- main.py continua chamando Base.metadata.create_all() no startup (cria tabelas)
- alembic stamp head (no Dockerfile) marca o DB como atualizado sem rodar SQL
- Futuras mudancas de schema viram migrations normais com autogenerate

Quando quiser migrar 100% pra Alembic:
1. Drop o DB
2. Remover Base.metadata.create_all() do main.py
3. Gerar nova migration inicial: alembic revision --autogenerate -m "schema completo"
4. alembic upgrade head
"""
from typing import Sequence, Union

from alembic import op  # noqa
import sqlalchemy as sa  # noqa


# revision identifiers, used by Alembic.
revision: str = 'f6648415e873'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Baseline - no-op (tabelas criadas via Base.metadata.create_all em main.py)."""
    pass


def downgrade() -> None:
    """Baseline - no-op."""
    pass
