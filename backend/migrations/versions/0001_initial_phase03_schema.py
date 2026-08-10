"""initial phase 03 schema

Revision ID: 0001_initial_phase03_schema
Revises: 
Create Date: 2026-08-10 00:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


revision = "0001_initial_phase03_schema"
down_revision = None
branch_labels = None
depends_on = None


source_type_enum = sa.Enum("VIDEO_FILE", "WEBCAM", "RTSP", name="sourcetype")
camera_status_enum = sa.Enum("ONLINE", "OFFLINE", "UNKNOWN", name="camerastatus")
zone_type_enum = sa.Enum("RESTRICTED", "LOITERING", "LINE_CROSSING", name="zonetype")
event_type_enum = sa.Enum("INTRUSION", "LINE_CROSSING", "LOITERING", name="eventtype")
severity_enum = sa.Enum("INFO", "WARNING", "CRITICAL", name="severitylevel")


def upgrade() -> None:
    op.create_table(
        "locations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.Text(), nullable=False, unique=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "cameras",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("location_id", sa.Integer(), sa.ForeignKey("locations.id", ondelete="SET NULL"), nullable=True),
        sa.Column("source_type", source_type_enum, nullable=False),
        sa.Column("source_uri", sa.Text(), nullable=False),
        sa.Column("status", camera_status_enum, nullable=False, server_default="UNKNOWN"),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_index(op.f("ix_cameras_id"), "cameras", ["id"], unique=False)

    op.create_table(
        "zones",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("camera_id", sa.Integer(), sa.ForeignKey("cameras.id", ondelete="SET NULL"), nullable=True),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("zone_type", zone_type_enum, nullable=False),
        sa.Column("coordinates", sa.JSON(), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_index(op.f("ix_zones_id"), "zones", ["id"], unique=False)

    op.create_table(
        "events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("camera_id", sa.Integer(), sa.ForeignKey("cameras.id", ondelete="SET NULL"), nullable=True),
        sa.Column("event_type", event_type_enum, nullable=False),
        sa.Column("severity", severity_enum, nullable=False, server_default="INFO"),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("track_id", sa.Integer(), nullable=True),
        sa.Column("object_class", sa.Text(), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column("snapshot_path", sa.Text(), nullable=True),
        sa.Column("video_path", sa.Text(), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=False, server_default=sa.text("'{}'")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_index(op.f("ix_events_id"), "events", ["id"], unique=False)
    op.create_index(op.f("ix_events_timestamp"), "events", ["timestamp"], unique=False)

    op.create_table(
        "recordings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("camera_id", sa.Integer(), sa.ForeignKey("cameras.id", ondelete="SET NULL"), nullable=True),
        sa.Column("event_id", sa.Integer(), sa.ForeignKey("events.id", ondelete="SET NULL"), nullable=True),
        sa.Column("file_path", sa.Text(), nullable=False),
        sa.Column("start_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_index(op.f("ix_recordings_id"), "recordings", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_recordings_id"), table_name="recordings")
    op.drop_table("recordings")
    op.drop_index(op.f("ix_events_timestamp"), table_name="events")
    op.drop_index(op.f("ix_events_id"), table_name="events")
    op.drop_table("events")
    op.drop_index(op.f("ix_zones_id"), table_name="zones")
    op.drop_table("zones")
    op.drop_index(op.f("ix_cameras_id"), table_name="cameras")
    op.drop_table("cameras")
    op.drop_table("locations")