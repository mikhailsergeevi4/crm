"""empty message

Revision ID: 2d9b00a43fe8
Revises: 2ea50ba912e5
Create Date: 2018-04-19 14:20:09.681419

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2d9b00a43fe8'
down_revision = '2ea50ba912e5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('do_not_forget',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('notes', sa.String(length=250), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('do_not_forget', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_do_not_forget_notes'), ['notes'], unique=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('do_not_forget', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_do_not_forget_notes'))

    op.drop_table('do_not_forget')
    # ### end Alembic commands ###
