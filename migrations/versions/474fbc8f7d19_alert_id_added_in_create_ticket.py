"""alert id added in create ticket

Revision ID: 474fbc8f7d19
Revises: 706ab6fe6eed
Create Date: 2025-01-06 14:10:19.779689

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '474fbc8f7d19'
down_revision = '706ab6fe6eed'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('SLA_log',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('customer_id', sa.Integer(), nullable=False),
    sa.Column('sub_customer_id', sa.Integer(), nullable=True),
    sa.Column('ticket_id', sa.Integer(), nullable=False),
    sa.Column('sla_start', sa.DateTime(), nullable=False),
    sa.Column('sla_due', sa.DateTime(), nullable=False),
    sa.Column('ticket_status', sa.String(length=255), nullable=False),
    sa.Column('sla_status', sa.String(length=255), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('is_encrypted', sa.Boolean(), nullable=False),
    sa.Column('sla_type', sa.String(length=255), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('SLA_log', schema=None) as batch_op:
        batch_op.create_index('sla_log_created_at', ['created_at'], unique=False)
        batch_op.create_index('sla_log_customer_id', ['customer_id'], unique=False)
        batch_op.create_index('sla_log_id', ['id'], unique=False)
        batch_op.create_index('sla_log_is_encrypted', ['is_encrypted'], unique=False)
        batch_op.create_index('sla_log_sla_due', ['sla_due'], unique=False)
        batch_op.create_index('sla_log_sla_start', ['sla_start'], unique=False)
        batch_op.create_index('sla_log_sla_status', ['sla_status'], unique=False)
        batch_op.create_index('sla_log_sla_type', ['sla_type'], unique=False)
        batch_op.create_index('sla_log_sub_customer_id', ['sub_customer_id'], unique=False)
        batch_op.create_index('sla_log_ticket_id', ['ticket_id'], unique=False)
        batch_op.create_index('sla_log_ticket_status', ['ticket_status'], unique=False)

    op.create_table('SLA_master',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('customer_id', sa.Integer(), nullable=False),
    sa.Column('sub_customer_id', sa.Integer(), nullable=True),
    sa.Column('severity', sa.String(length=255), nullable=True),
    sa.Column('priority', sa.String(length=255), nullable=True),
    sa.Column('ticket_type', sa.String(length=255), nullable=True),
    sa.Column('response_time_sla', sa.Integer(), nullable=True),
    sa.Column('resolve_time_sla', sa.Integer(), nullable=True),
    sa.Column('business_hr_bypass', sa.String(length=255), nullable=True),
    sa.Column('holiday_hour_bypass', sa.String(length=255), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('is_encrypted', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('SLA_master', schema=None) as batch_op:
        batch_op.create_index('sla_master_business_hr_bypass', ['business_hr_bypass'], unique=False)
        batch_op.create_index('sla_master_created_at', ['created_at'], unique=False)
        batch_op.create_index('sla_master_customer_id', ['customer_id'], unique=False)
        batch_op.create_index('sla_master_holiday_hour_bypass', ['holiday_hour_bypass'], unique=False)
        batch_op.create_index('sla_master_id', ['id'], unique=False)
        batch_op.create_index('sla_master_is_encrypted', ['is_encrypted'], unique=False)
        batch_op.create_index('sla_master_priority', ['priority'], unique=False)
        batch_op.create_index('sla_master_resolve_time_sla', ['resolve_time_sla'], unique=False)
        batch_op.create_index('sla_master_response_time_sla', ['response_time_sla'], unique=False)
        batch_op.create_index('sla_master_severity', ['severity'], unique=False)
        batch_op.create_index('sla_master_sub_customer_id', ['sub_customer_id'], unique=False)
        batch_op.create_index('sla_master_ticket_type', ['ticket_type'], unique=False)

    with op.batch_alter_table('sla_master', schema=None) as batch_op:
        batch_op.drop_index('sla_master_business_hr_bypass')
        batch_op.drop_index('sla_master_created_at')
        batch_op.drop_index('sla_master_customer_id')
        batch_op.drop_index('sla_master_holiday_hour_bypass')
        batch_op.drop_index('sla_master_id')
        batch_op.drop_index('sla_master_is_encrypted')
        batch_op.drop_index('sla_master_priority')
        batch_op.drop_index('sla_master_resolve_time_sla')
        batch_op.drop_index('sla_master_response_time_sla')
        batch_op.drop_index('sla_master_severity')
        batch_op.drop_index('sla_master_sub_customer_id')
        batch_op.drop_index('sla_master_ticket_type')

    op.drop_table('sla_master')
    with op.batch_alter_table('sla_log', schema=None) as batch_op:
        batch_op.drop_index('sla_log_created_at')
        batch_op.drop_index('sla_log_customer_id')
        batch_op.drop_index('sla_log_id')
        batch_op.drop_index('sla_log_is_encrypted')
        batch_op.drop_index('sla_log_sla_due')
        batch_op.drop_index('sla_log_sla_start')
        batch_op.drop_index('sla_log_sla_status')
        batch_op.drop_index('sla_log_sla_type')
        batch_op.drop_index('sla_log_sub_customer_id')
        batch_op.drop_index('sla_log_ticket_id')
        batch_op.drop_index('sla_log_ticket_status')

    op.drop_table('sla_log')
    with op.batch_alter_table('ticket_master', schema=None) as batch_op:
        batch_op.add_column(sa.Column('alert_id', sa.String(length=255), nullable=True))
        batch_op.create_index('ticket_master_alert_id', ['alert_id'], unique=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('ticket_master', schema=None) as batch_op:
        batch_op.drop_index('ticket_master_alert_id')
        batch_op.drop_column('alert_id')

    op.create_table('sla_log',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('customer_id', mysql.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('sub_customer_id', mysql.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('ticket_id', mysql.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('sla_start', mysql.DATETIME(), nullable=False),
    sa.Column('sla_due', mysql.DATETIME(), nullable=False),
    sa.Column('ticket_status', mysql.VARCHAR(length=255), nullable=False),
    sa.Column('sla_status', mysql.VARCHAR(length=255), nullable=False),
    sa.Column('created_at', mysql.DATETIME(), nullable=False),
    sa.Column('is_encrypted', mysql.TINYINT(display_width=1), autoincrement=False, nullable=False),
    sa.Column('sla_type', mysql.VARCHAR(length=255), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    with op.batch_alter_table('sla_log', schema=None) as batch_op:
        batch_op.create_index('sla_log_ticket_status', ['ticket_status'], unique=False)
        batch_op.create_index('sla_log_ticket_id', ['ticket_id'], unique=False)
        batch_op.create_index('sla_log_sub_customer_id', ['sub_customer_id'], unique=False)
        batch_op.create_index('sla_log_sla_type', ['sla_type'], unique=False)
        batch_op.create_index('sla_log_sla_status', ['sla_status'], unique=False)
        batch_op.create_index('sla_log_sla_start', ['sla_start'], unique=False)
        batch_op.create_index('sla_log_sla_due', ['sla_due'], unique=False)
        batch_op.create_index('sla_log_is_encrypted', ['is_encrypted'], unique=False)
        batch_op.create_index('sla_log_id', ['id'], unique=False)
        batch_op.create_index('sla_log_customer_id', ['customer_id'], unique=False)
        batch_op.create_index('sla_log_created_at', ['created_at'], unique=False)

    op.create_table('sla_master',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('customer_id', mysql.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('sub_customer_id', mysql.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('severity', mysql.VARCHAR(length=255), nullable=True),
    sa.Column('priority', mysql.VARCHAR(length=255), nullable=True),
    sa.Column('ticket_type', mysql.VARCHAR(length=255), nullable=True),
    sa.Column('response_time_sla', mysql.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('resolve_time_sla', mysql.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('business_hr_bypass', mysql.VARCHAR(length=255), nullable=True),
    sa.Column('holiday_hour_bypass', mysql.VARCHAR(length=255), nullable=True),
    sa.Column('created_at', mysql.DATETIME(), nullable=False),
    sa.Column('is_encrypted', mysql.TINYINT(display_width=1), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    with op.batch_alter_table('sla_master', schema=None) as batch_op:
        batch_op.create_index('sla_master_ticket_type', ['ticket_type'], unique=False)
        batch_op.create_index('sla_master_sub_customer_id', ['sub_customer_id'], unique=False)
        batch_op.create_index('sla_master_severity', ['severity'], unique=False)
        batch_op.create_index('sla_master_response_time_sla', ['response_time_sla'], unique=False)
        batch_op.create_index('sla_master_resolve_time_sla', ['resolve_time_sla'], unique=False)
        batch_op.create_index('sla_master_priority', ['priority'], unique=False)
        batch_op.create_index('sla_master_is_encrypted', ['is_encrypted'], unique=False)
        batch_op.create_index('sla_master_id', ['id'], unique=False)
        batch_op.create_index('sla_master_holiday_hour_bypass', ['holiday_hour_bypass'], unique=False)
        batch_op.create_index('sla_master_customer_id', ['customer_id'], unique=False)
        batch_op.create_index('sla_master_created_at', ['created_at'], unique=False)
        batch_op.create_index('sla_master_business_hr_bypass', ['business_hr_bypass'], unique=False)

    with op.batch_alter_table('SLA_master', schema=None) as batch_op:
        batch_op.drop_index('sla_master_ticket_type')
        batch_op.drop_index('sla_master_sub_customer_id')
        batch_op.drop_index('sla_master_severity')
        batch_op.drop_index('sla_master_response_time_sla')
        batch_op.drop_index('sla_master_resolve_time_sla')
        batch_op.drop_index('sla_master_priority')
        batch_op.drop_index('sla_master_is_encrypted')
        batch_op.drop_index('sla_master_id')
        batch_op.drop_index('sla_master_holiday_hour_bypass')
        batch_op.drop_index('sla_master_customer_id')
        batch_op.drop_index('sla_master_created_at')
        batch_op.drop_index('sla_master_business_hr_bypass')

    op.drop_table('SLA_master')
    with op.batch_alter_table('SLA_log', schema=None) as batch_op:
        batch_op.drop_index('sla_log_ticket_status')
        batch_op.drop_index('sla_log_ticket_id')
        batch_op.drop_index('sla_log_sub_customer_id')
        batch_op.drop_index('sla_log_sla_type')
        batch_op.drop_index('sla_log_sla_status')
        batch_op.drop_index('sla_log_sla_start')
        batch_op.drop_index('sla_log_sla_due')
        batch_op.drop_index('sla_log_is_encrypted')
        batch_op.drop_index('sla_log_id')
        batch_op.drop_index('sla_log_customer_id')
        batch_op.drop_index('sla_log_created_at')

    op.drop_table('SLA_log')
    # ### end Alembic commands ###
