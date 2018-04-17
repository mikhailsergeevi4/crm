"""notes for Contract

Revision ID: 2d48725d4f05
Revises: a3058fd9fb99
Create Date: 2018-04-17 10:59:55.055443

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2d48725d4f05'
down_revision = 'a3058fd9fb99'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('contract', schema=None) as batch_op:
        batch_op.add_column(sa.Column('notes', sa.String(length=250), nullable=True))
        batch_op.create_index(batch_op.f('ix_contract_notes'), ['notes'], unique=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('contract', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_contract_notes'))
        batch_op.drop_column('notes')

    # ### end Alembic commands ###
