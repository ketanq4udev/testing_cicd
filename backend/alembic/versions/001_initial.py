"""initial schema

Revision ID: 001
Revises:
Create Date: 2026-01-01 00:00:00.000000
"""
revision = "001"
down_revision = None
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        "items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.String(), server_default=""),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_items_id"), "items", ["id"], unique=False)

    op.bulk_insert(
        sa.table(
            "items",
            sa.column("name", sa.String),
            sa.column("description", sa.String),
        ),
        [
            {"name": "Item One", "description": "First sample item"},
            {"name": "Item Two", "description": "Second sample item"},
        ],
    )


def downgrade():
    op.drop_index(op.f("ix_items_id"), table_name="items")
    op.drop_table("items")
