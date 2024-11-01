"""New column to the contracts table

Revision ID: 06383cfd559e
Revises: c2dcb4f82c5f
Create Date: 2024-10-28 15:18:36.027376

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '06383cfd559e'
down_revision = 'c2dcb4f82c5f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('contracts', schema=None) as batch_op:
        batch_op.add_column(sa.Column('comments', sa.TEXT(), nullable=True))

    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column('password',
               existing_type=sa.VARCHAR(length=8),
               type_=sa.CHAR(length=12),
               existing_nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column('password',
               existing_type=sa.CHAR(length=12),
               type_=sa.VARCHAR(length=8),
               existing_nullable=False)

    with op.batch_alter_table('contracts', schema=None) as batch_op:
        batch_op.drop_column('comments')

    # ### end Alembic commands ###