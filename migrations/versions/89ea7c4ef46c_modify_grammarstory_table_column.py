"""modify grammarstory table column

Revision ID: 89ea7c4ef46c
Revises: 0bf1e6139c39
Create Date: 2018-10-21 09:44:23.788310

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '89ea7c4ef46c'
down_revision = '0bf1e6139c39'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('grammar_story', schema=None) as batch_op:
        batch_op.add_column(sa.Column('rules', sa.String(length=25), nullable=True))
        batch_op.add_column(sa.Column('story', sa.String(length=10000), nullable=True))
        batch_op.drop_column('sentence')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('grammar_story', schema=None) as batch_op:
        batch_op.add_column(sa.Column('sentence', sa.VARCHAR(length=1000), nullable=True))
        batch_op.drop_column('story')
        batch_op.drop_column('rules')

    # ### end Alembic commands ###