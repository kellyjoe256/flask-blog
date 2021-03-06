"""empty message

Revision ID: 85913886b640
Revises: 
Create Date: 2018-12-14 23:44:36.834542

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '85913886b640'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('tag',
    sa.Column('tag_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=30), nullable=False),
    sa.Column('slug', sa.String(length=45), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('tag_id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('user',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=120), nullable=False),
    sa.Column('username', sa.String(length=30), nullable=False),
    sa.Column('email', sa.String(length=50), nullable=False),
    sa.Column('salt', sa.String(length=32), nullable=True),
    sa.Column('hashed_password', sa.String(length=128), nullable=True),
    sa.Column('is_admin', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('user_id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('username')
    )
    op.create_table('post',
    sa.Column('post_id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=255), nullable=False),
    sa.Column('slug', sa.String(length=300), nullable=False),
    sa.Column('content', sa.Text(), nullable=False),
    sa.Column('content_html', sa.Text(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.user_id'], ),
    sa.PrimaryKeyConstraint('post_id')
    )
    op.create_table('post_tag',
    sa.Column('tag_id', sa.Integer(), nullable=False),
    sa.Column('page_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['page_id'], ['post.post_id'], ),
    sa.ForeignKeyConstraint(['tag_id'], ['tag.tag_id'], ),
    sa.PrimaryKeyConstraint('tag_id', 'page_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('post_tag')
    op.drop_table('post')
    op.drop_table('user')
    op.drop_table('tag')
    # ### end Alembic commands ###
