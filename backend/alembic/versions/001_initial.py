"""Initial migration

Revision ID: 001
Revises: 
Create Date: 2025-03-25

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'districts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('state', sa.String(length=100), nullable=True, server_default='Andhra Pradesh'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    op.create_index(op.f('ix_districts_id'), 'districts', ['id'], unique=False)

    op.create_table(
        'stakeholders',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('type', sa.Enum('SUPPLIER', 'TRANSPORT_FLEET', 'AWW', 'CDPO', 'SUPERVISOR', 'COLLECTOR', 'SECRETARY', name='stakeholdertype'), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('district_id', sa.Integer(), nullable=True),
        sa.Column('block_id', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['district_id'], ['districts.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_stakeholders_id'), 'stakeholders', ['id'], unique=False)

    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=False),
        sa.Column('role', sa.Enum('STATE_ADMIN', 'DISTRICT_ADMIN', 'BLOCK_SUPERVISOR', 'AWW', 'SUPPLIER', 'TRANSPORTER', name='userrole'), nullable=True, server_default='AWW'),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('stakeholder_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['stakeholder_id'], ['stakeholders.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)

    op.create_table(
        'blocks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('district_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['district_id'], ['districts.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    op.create_index(op.f('ix_blocks_id'), 'blocks', ['id'], unique=False)

    op.create_table(
        'suppliers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('contact_person', sa.String(length=255), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('district_id', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['district_id'], ['districts.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    op.create_index(op.f('ix_suppliers_id'), 'suppliers', ['id'], unique=False)

    op.create_table(
        'warehouses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('district_id', sa.Integer(), nullable=False),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('latitude', sa.Numeric(precision=10, scale=8), nullable=True),
        sa.Column('longitude', sa.Numeric(precision=11, scale=8), nullable=True),
        sa.Column('capacity_mt', sa.Numeric(precision=10, scale=2), nullable=True, server_default='0'),
        sa.Column('current_stock_mt', sa.Numeric(precision=10, scale=2), nullable=True, server_default='0'),
        sa.Column('manager_name', sa.String(length=255), nullable=True),
        sa.Column('manager_phone', sa.String(length=20), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['district_id'], ['districts.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    op.create_index(op.f('ix_warehouses_id'), 'warehouses', ['id'], unique=False)

    op.create_table(
        'villages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('block_id', sa.Integer(), nullable=False),
        sa.Column('latitude', sa.Numeric(precision=10, scale=8), nullable=True),
        sa.Column('longitude', sa.Numeric(precision=11, scale=8), nullable=True),
        sa.Column('population', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['block_id'], ['blocks.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    op.create_index(op.f('ix_villages_id'), 'villages', ['id'], unique=False)

    op.create_table(
        'supply_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=False),
        sa.Column('unit', sa.String(length=50), nullable=True, server_default='kg'),
        sa.Column('unit_price', sa.Numeric(precision=10, scale=2), nullable=True, server_default='0'),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    op.create_index(op.f('ix_supply_items_id'), 'supply_items', ['id'], unique=False)

    op.create_table(
        'transport_fleets',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('vehicle_number', sa.String(length=50), nullable=False),
        sa.Column('vehicle_type', sa.String(length=100), nullable=False),
        sa.Column('driver_name', sa.String(length=255), nullable=True),
        sa.Column('driver_phone', sa.String(length=20), nullable=True),
        sa.Column('capacity_kg', sa.Numeric(precision=10, scale=2), nullable=True, server_default='0'),
        sa.Column('warehouse_id', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['warehouse_id'], ['warehouses.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('vehicle_number')
    )
    op.create_index(op.f('ix_transport_fleets_id'), 'transport_fleets', ['id'], unique=False)

    op.create_table(
        'anganwadi_centers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('village_id', sa.Integer(), nullable=False),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('latitude', sa.Numeric(precision=10, scale=8), nullable=True),
        sa.Column('longitude', sa.Numeric(precision=11, scale=8), nullable=True),
        sa.Column('aww_name', sa.String(length=255), nullable=True),
        sa.Column('aww_phone', sa.String(length=20), nullable=True),
        sa.Column('total_beneficiaries', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('children_0_3', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('children_3_6', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('pregnant_women', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('lactating_mothers', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['village_id'], ['villages.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    op.create_index(op.f('ix_anganwadi_centers_id'), 'anganwadi_centers', ['id'], unique=False)

    op.create_table(
        'inventory',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('item_id', sa.Integer(), nullable=False),
        sa.Column('warehouse_id', sa.Integer(), nullable=True),
        sa.Column('anganwadi_center_id', sa.Integer(), nullable=True),
        sa.Column('quantity', sa.Numeric(precision=10, scale=2), nullable=True, server_default='0'),
        sa.Column('min_threshold', sa.Numeric(precision=10, scale=2), nullable=True, server_default='0'),
        sa.Column('max_threshold', sa.Numeric(precision=10, scale=2), nullable=True, server_default='0'),
        sa.Column('last_updated', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['item_id'], ['supply_items.id'], ),
        sa.ForeignKeyConstraint(['warehouse_id'], ['warehouses.id'], ),
        sa.ForeignKeyConstraint(['anganwadi_center_id'], ['anganwadi_centers.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_inventory_id'), 'inventory', ['id'], unique=False)

    op.create_table(
        'routes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('warehouse_id', sa.Integer(), nullable=False),
        sa.Column('transport_fleet_id', sa.Integer(), nullable=True),
        sa.Column('total_distance_km', sa.Numeric(precision=10, scale=2), nullable=True, server_default='0'),
        sa.Column('estimated_time_minutes', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('stops_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('waypoints', sa.Text(), nullable=True),
        sa.Column('is_optimized', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['warehouse_id'], ['warehouses.id'], ),
        sa.ForeignKeyConstraint(['transport_fleet_id'], ['transport_fleets.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_routes_id'), 'routes', ['id'], unique=False)

    op.create_table(
        'deliveries',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tracking_code', sa.String(length=50), nullable=False),
        sa.Column('warehouse_id', sa.Integer(), nullable=False),
        sa.Column('anganwadi_center_id', sa.Integer(), nullable=False),
        sa.Column('transport_fleet_id', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True, server_default='pending'),
        sa.Column('scheduled_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('delivered_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('total_weight_kg', sa.Numeric(precision=10, scale=2), nullable=True, server_default='0'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['warehouse_id'], ['warehouses.id'], ),
        sa.ForeignKeyConstraint(['anganwadi_center_id'], ['anganwadi_centers.id'], ),
        sa.ForeignKeyConstraint(['transport_fleet_id'], ['transport_fleets.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tracking_code')
    )
    op.create_index(op.f('ix_deliveries_id'), 'deliveries', ['id'], unique=False)

    op.create_table(
        'grievances',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('ticket_number', sa.String(length=50), nullable=False),
        sa.Column('submitted_by_id', sa.Integer(), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=False),
        sa.Column('priority', sa.String(length=50), nullable=True, server_default='medium'),
        sa.Column('status', sa.String(length=50), nullable=True, server_default='open'),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('ai_analysis', sa.Text(), nullable=True),
        sa.Column('sentiment_score', sa.Numeric(precision=3, scale=2), nullable=True),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('resolution_notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['submitted_by_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('ticket_number')
    )
    op.create_index(op.f('ix_grievances_id'), 'grievances', ['id'], unique=False)

    op.create_table(
        'trust_scores',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('stakeholder_id', sa.Integer(), nullable=False),
        sa.Column('score', sa.Numeric(precision=3, scale=2), nullable=True, server_default='0.00'),
        sa.Column('zone', sa.Enum('GREEN', 'YELLOW', 'ORANGE', 'RED', name='trustzone'), nullable=True, server_default='YELLOW'),
        sa.Column('delivery_performance', sa.Numeric(precision=3, scale=2), nullable=True, server_default='0.00'),
        sa.Column('quality_compliance', sa.Numeric(precision=3, scale=2), nullable=True, server_default='0.00'),
        sa.Column('grievance_rate', sa.Numeric(precision=3, scale=2), nullable=True, server_default='0.00'),
        sa.Column('data_accuracy', sa.Numeric(precision=3, scale=2), nullable=True, server_default='0.00'),
        sa.Column('calculated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['stakeholder_id'], ['stakeholders.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_trust_scores_id'), 'trust_scores', ['id'], unique=False)

    op.create_table(
        'audit_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('action', sa.String(length=100), nullable=False),
        sa.Column('entity_type', sa.String(length=100), nullable=False),
        sa.Column('entity_id', sa.Integer(), nullable=True),
        sa.Column('details', sa.Text(), nullable=True),
        sa.Column('ip_address', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_audit_logs_id'), 'audit_logs', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_audit_logs_id'), table_name='audit_logs')
    op.drop_table('audit_logs')

    op.drop_index(op.f('ix_trust_scores_id'), table_name='trust_scores')
    op.drop_table('trust_scores')

    op.drop_index(op.f('ix_grievances_id'), table_name='grievances')
    op.drop_table('grievances')

    op.drop_index(op.f('ix_deliveries_id'), table_name='deliveries')
    op.drop_table('deliveries')

    op.drop_index(op.f('ix_routes_id'), table_name='routes')
    op.drop_table('routes')

    op.drop_index(op.f('ix_inventory_id'), table_name='inventory')
    op.drop_table('inventory')

    op.drop_index(op.f('ix_anganwadi_centers_id'), table_name='anganwadi_centers')
    op.drop_table('anganwadi_centers')

    op.drop_index(op.f('ix_transport_fleets_id'), table_name='transport_fleets')
    op.drop_table('transport_fleets')

    op.drop_index(op.f('ix_supply_items_id'), table_name='supply_items')
    op.drop_table('supply_items')

    op.drop_index(op.f('ix_villages_id'), table_name='villages')
    op.drop_table('villages')

    op.drop_index(op.f('ix_warehouses_id'), table_name='warehouses')
    op.drop_table('warehouses')

    op.drop_index(op.f('ix_suppliers_id'), table_name='suppliers')
    op.drop_table('suppliers')

    op.drop_index(op.f('ix_blocks_id'), table_name='blocks')
    op.drop_table('blocks')

    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')

    op.drop_index(op.f('ix_stakeholders_id'), table_name='stakeholders')
    op.drop_table('stakeholders')

    op.drop_index(op.f('ix_districts_id'), table_name='districts')
    op.drop_table('districts')
