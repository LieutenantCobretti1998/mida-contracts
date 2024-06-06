"""Add cascade delete to contracts

Revision ID: 19398b765039
Revises: 90ac10b70f30
Create Date: 2024-06-06 21:17:37.155433

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '19398b765039'
down_revision = '90ac10b70f30'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("temp_contracts",
                    sa.Column("id", sa.Integer(), primary_key=True),
                    sa.Column("contract_number", sa.CHAR(16), nullable=False),
                    sa.Column("date", sa.Date(), nullable=False),
                    sa.Column("company_id", sa.Integer(), nullable=False),
                    sa.Column("amount", sa.DECIMAL(), nullable=False),
                    sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="CASCADE")
                    )

    conn = op.get_bind()
    conn.execute(
        sa.text(
            """
                INSERT INTO temp_contracts (id, contract_number, date, company_id, amount)
                SELECT id, contract_number, date, company_id, amount FROM contracts
            """
        )
    )
    # Drop the old table and rename the new table
    op.drop_table('contracts')
    op.rename_table('temp_contracts', 'contracts')


def downgrade():
    # This will recreate the 'contracts' table without the CASCADE option
    op.create_table('contracts',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('contract_number', sa.CHAR(length=16), nullable=False),
                    sa.Column('date', sa.DATE(), nullable=False),
                    sa.Column('company_id', sa.Integer(), nullable=False),
                    sa.Column('amount', sa.DECIMAL(), nullable=False),
                    sa.ForeignKeyConstraint(['company_id'], ['companies.id']),
                    sa.PrimaryKeyConstraint('id')
                    )

    # If applicable, copy data back to the original table structure
    # Note: This is tricky as it assumes no data loss, ensure backup before downgrade
    conn = op.get_bind()
    conn.execute(
        sa.text("""
                INSERT INTO contracts (id, contract_number, date, company_id, amount)
                SELECT id, contract_number, date, company_id, amount FROM temp_contracts
            """)
    )
    op.drop_table('temp_contracts')
