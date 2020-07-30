"""Change id to text instead of integer

Revision ID: a16cc4688a6e
Revises: 370d53e800de
Create Date: 2020-07-30 22:20:52.069405

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a16cc4688a6e'
down_revision = '370d53e800de'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('shortURL', sa.Column('short_code', sa.Text(), nullable=False))
    op.drop_column('shortURL', 'id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('shortURL', sa.Column('id', sa.INTEGER(), server_default=sa.text('nextval(\'"shortURL_id_seq"\'::regclass)'), autoincrement=True, nullable=False))
    op.drop_column('shortURL', 'short_code')
    # ### end Alembic commands ###
