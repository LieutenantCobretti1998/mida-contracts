"""Adding some new column to company table.

Revision ID: 3b0a11e708a1
Revises: c5e4afe62e09
Create Date: 2024-06-18 11:10:00.106956

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3b0a11e708a1'
down_revision = 'c5e4afe62e09'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('companies', schema=None) as batch_op:
        batch_op.add_column(sa.Column('email', sa.VARCHAR(), nullable=True))
        batch_op.add_column(sa.Column('telephone_number', sa.VARCHAR(), nullable=True))
        batch_op.add_column(sa.Column('address', sa.VARCHAR(), nullable=True))
        batch_op.add_column(sa.Column('website', sa.VARCHAR(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###

    with op.batch_alter_table('companies', schema=None) as batch_op:
        batch_op.drop_column('email')
        batch_op.drop_column('telephone_number')
        batch_op.drop_column('address')
        batch_op.drop_column('website')

    # ### end Alembic commands ###
