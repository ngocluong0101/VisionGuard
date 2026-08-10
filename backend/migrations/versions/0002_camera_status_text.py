"""camera status text

Revision ID: 0002_camera_status_text
Revises: 0001_initial_phase03_schema
Create Date: 2026-08-10 00:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


revision = "0002_camera_status_text"
down_revision = "0001_initial_phase03_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("cameras") as batch_op:
        batch_op.alter_column(
            "status",
            existing_type=sa.String(length=32),
            type_=sa.Text(),
            existing_nullable=False,
            existing_server_default="UNKNOWN",
        )


def downgrade() -> None:
    with op.batch_alter_table("cameras") as batch_op:
        batch_op.alter_column(
            "status",
            existing_type=sa.Text(),
            type_=sa.String(length=32),
            existing_nullable=False,
            existing_server_default="UNKNOWN",
        )