"""empty message

Revision ID: 661c079fe203
Revises: 85913886b640
Create Date: 2018-12-17 10:02:42.612909

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '661c079fe203'
down_revision = '85913886b640'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('active', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'active')
    # ### end Alembic commands ###
