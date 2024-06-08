"""Add pdf_file_path to contracts and update data types

Revision ID: c5e4afe62e09
Revises: 19398b765039
Create Date: 2024-06-08 18:47:33.227884

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c5e4afe62e09'
down_revision = '19398b765039'
branch_labels = None
depends_on = None


def upgrade():
    # Create a new temporary table with the correct schema and constraints
    op.create_table('temp_contracts',
                    sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
                    sa.Column('contract_number', sa.VARCHAR(length=16), nullable=False),
                    sa.Column('date', sa.DATE(), nullable=False),
                    sa.Column('company_id', sa.Integer(), nullable=False),
                    sa.Column('amount', sa.DECIMAL(), nullable=False),
                    sa.Column('pdf_file_path', sa.VARCHAR(), nullable=False, default="path"),
                    sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE')
                    )

    # Copy data from the old table to the new table
    conn = op.get_bind()
    conn.execute(
        sa.text("""
                INSERT INTO temp_contracts (id, contract_number, date, company_id, amount, pdf_file_path)
                SELECT id, contract_number, date, company_id, amount, "default.pdf" FROM contracts
            """)
    )

    # Drop the old table and rename the new table
    op.drop_table('contracts')
    op.rename_table('temp_contracts', 'contracts')

    # Adjusting columns in 'companies' table
    with op.batch_alter_table('companies', schema=None) as batch_op:
        batch_op.alter_column('voen',
                              existing_type=sa.CHAR(length=20),
                              type_=sa.CHAR(length=10),
                              existing_nullable=False)
        batch_op.alter_column('company_name',
                              existing_type=sa.CHAR(length=16),
                              type_=sa.VARCHAR(length=16),
                              existing_nullable=False)


def downgrade():
    # Create the original contracts table
    op.create_table('temp_contracts',
                    sa.Column('id', sa.Integer(), primary_key=True),
                    sa.Column('contract_number', sa.CHAR(length=16), nullable=False),
                    sa.Column('date', sa.DATE(), nullable=False),
                    sa.Column('company_id', sa.Integer(), nullable=False),
                    sa.Column('amount', sa.DECIMAL(), nullable=False),
                    sa.ForeignKeyConstraint(['company_id'], ['companies.id'])
                    )

    # Copy data back from the new table to the old table
    conn = op.get_bind()
    conn.execute(
        sa.text("""
                INSERT INTO temp_contracts (id, contract_number, date, company_id, amount)
                SELECT id, contract_number, date, company_id, amount FROM contracts
            """)
    )

    # Drop the new table and rename the old table
    op.drop_table('contracts')
    op.rename_table('temp_contracts', 'contracts')

    # Adjusting columns in 'companies' table
    with op.batch_alter_table('companies', schema=None) as batch_op:
        batch_op.alter_column('voen',
                              existing_type=sa.CHAR(length=10),
                              type_=sa.CHAR(length=20),
                              existing_nullable=False)
        batch_op.alter_column('company_name',
                              existing_type=sa.VARCHAR(length=16),
                              type_=sa.CHAR(length=16),
                              existing_nullable=False)
