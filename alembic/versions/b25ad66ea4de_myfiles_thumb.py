"""myfiles_thumb

Revision ID: b25ad66ea4de
Revises: bf74339902fd
Create Date: 2017-01-10 16:18:22.928798

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b25ad66ea4de'
down_revision = 'bf74339902fd'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('myfiles', schema=None) as batch_op:
        batch_op.add_column(sa.Column('_thumb', sa.String(length=512), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('myfiles', schema=None) as batch_op:
        batch_op.drop_column('_thumb')

    # ### end Alembic commands ###