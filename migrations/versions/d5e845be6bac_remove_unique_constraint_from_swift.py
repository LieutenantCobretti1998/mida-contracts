"""Remove unique constraint from Swift

Revision ID: d5e845be6bac
Revises: 91cf43f70076
Create Date: 2025-03-11 15:32:22.392249

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd5e845be6bac'
down_revision = '91cf43f70076'
branch_labels = None
depends_on = None


def upgrade():
    # Create a new table without unique constraint on swift.
    op.create_table(
        'companies_new',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('company_name', sa.VARCHAR(16), nullable=False),
        sa.Column('voen', sa.CHAR(10), nullable=False, unique=True),
        sa.Column('bank_name', sa.VARCHAR()),
        sa.Column('m_h', sa.VARCHAR()),
        sa.Column('h_h', sa.VARCHAR()),
        # Remove unique=True for swift here:
        sa.Column('swift', sa.VARCHAR(11), nullable=True),
        sa.Column('email', sa.VARCHAR()),
        sa.Column('telephone_number', sa.VARCHAR()),
        sa.Column('address', sa.VARCHAR()),
        sa.Column('website', sa.VARCHAR())
    )

    # Copy data from old table to new table.
    op.execute(
        """
        INSERT INTO companies_new (id, company_name, voen, bank_name, m_h, h_h, swift, email, telephone_number, address, website)
        SELECT id, company_name, voen, bank_name, m_h, h_h, swift, email, telephone_number, address, website
        FROM companies;
        """
    )

    # Drop the old table.
    op.drop_table('companies')
    # Rename the new table to the old table name.
    op.rename_table('companies_new', 'companies')


def downgrade():
    # If you need to revert, recreate the table with the unique constraint on swift.
    op.create_table(
        'companies_new',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('company_name', sa.VARCHAR(16), nullable=False),
        sa.Column('voen', sa.CHAR(10), nullable=False, unique=True),
        sa.Column('bank_name', sa.VARCHAR()),
        sa.Column('m_h', sa.VARCHAR()),
        sa.Column('h_h', sa.VARCHAR()),
        # Restore the unique constraint on swift:
        sa.Column('swift', sa.VARCHAR(11), nullable=True, unique=True),
        sa.Column('email', sa.VARCHAR()),
        sa.Column('telephone_number', sa.VARCHAR()),
        sa.Column('address', sa.VARCHAR()),
        sa.Column('website', sa.VARCHAR())
    )

    op.execute(
        """
        INSERT INTO companies_new (id, company_name, voen, bank_name, m_h, h_h, swift, email, telephone_number, address, website)
        SELECT id, company_name, voen, bank_name, m_h, h_h, swift, email, telephone_number, address, website
        FROM companies;
        """
    )

    op.drop_table('companies')
    op.rename_table('companies_new', 'companies')
