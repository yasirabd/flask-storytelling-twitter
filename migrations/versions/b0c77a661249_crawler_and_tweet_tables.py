"""crawler and tweet tables

Revision ID: b0c77a661249
Revises: 
Create Date: 2018-05-02 13:12:52.598188

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b0c77a661249'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('crawler',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_crawler_timestamp'), 'crawler', ['timestamp'], unique=False)
    op.create_table('tweet',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.String(length=50), nullable=True),
    sa.Column('username', sa.String(length=50), nullable=True),
    sa.Column('created', sa.DateTime(), nullable=True),
    sa.Column('text', sa.String(length=200), nullable=True),
    sa.Column('latitude', sa.Text(), nullable=True),
    sa.Column('longitude', sa.Text(), nullable=True),
    sa.Column('crawler_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['crawler_id'], ['crawler.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('tweet')
    op.drop_index(op.f('ix_crawler_timestamp'), table_name='crawler')
    op.drop_table('crawler')
    # ### end Alembic commands ###