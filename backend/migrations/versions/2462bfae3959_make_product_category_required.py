"""make product category required

Revision ID: 2462bfae3959
Revises: c3e6af021d77
Create Date: 2026-10-23 15:41:09.418319

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2462bfae3959'
down_revision: Union[str, Sequence[str], None] = 'c3e6af021d77'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        INSERT INTO categories (id, name, slug, parent_id)
        VALUES (
            '00000000-0000-0000-0000-000000000001',
            'Без категории',
            'uncategorized',
            NULL
        )
        ON CONFLICT (slug) DO NOTHING
    """)

    op.execute("""
        UPDATE products
        SET category_id = (
            SELECT id
            FROM categories
            WHERE slug = 'uncategorized'
        )
        WHERE category_id IS NULL
    """)

    op.alter_column(
        "products",
        "category_id",
        existing_type=sa.UUID(),
        nullable=False,
    )

    op.drop_constraint(
        "products_category_id_fkey",
        "products",
        type_="foreignkey",
    )

    op.create_foreign_key(
        "products_category_id_fkey",
        "products",
        "categories",
        ["category_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    pass


def downgrade() -> None:
    op.drop_constraint(
        "products_category_id_fkey",
        "products",
        type_="foreignkey",
    )

    op.create_foreign_key(
        "products_category_id_fkey",
        "products",
        "categories",
        ["category_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.alter_column(
        "products",
        "category_id",
        existing_type=sa.UUID(),
        nullable=True,
    )
    pass
