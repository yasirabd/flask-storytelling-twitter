"""add crawler_id field in preprocess table

Revision ID: adcbcecbcfe9
Revises: ec3c1e4661ca
Create Date: 2018-06-24 20:58:24.074444

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'adcbcecbcfe9'
down_revision = 'ec3c1e4661ca'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('preprocess', schema=None) as batch_op:
        batch_op.create_foreign_key(batch_op.f('fk_preprocess_crawler_id_crawler'), 'crawler', ['crawler_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('preprocess', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('fk_preprocess_crawler_id_crawler'), type_='foreignkey')

    # ### end Alembic commands ###
