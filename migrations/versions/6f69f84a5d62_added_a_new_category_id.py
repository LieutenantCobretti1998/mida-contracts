"""Added a new category id

Revision ID: 6f69f84a5d62
Revises: 03db6dea2c5e
Create Date: 2024-08-12 15:39:02.664125

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6f69f84a5d62'
down_revision = '03db6dea2c5e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###

    naming_convention = {
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    }

    with op.batch_alter_table('contracts', schema=None, naming_convention=naming_convention) as batch_op:
        batch_op.add_column(sa.Column('category_id', sa.Integer(), nullable=False))
        batch_op.create_foreign_key('fk_contracts_category_id_categories', 'categories', ['category_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('contracts', schema=None) as batch_op:
        batch_op.drop_constraint('fk_contracts_category_id_categories', type_='foreignkey')
        batch_op.drop_column('category_id')

    # ### end Alembic commands ###