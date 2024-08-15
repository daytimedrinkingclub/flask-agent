"""Initial Migration

Revision ID: 697fd1f47479
Revises: 
Create Date: 2024-07-11 16:17:12.626097

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '697fd1f47479'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('username', sa.String(length=64), nullable=False),
    sa.Column('password_hash', sa.String(length=10000), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('username')
    )
    op.create_table('chat',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('botnine_chatbot_id', sa.String(length=256), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('token',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('botnine_token', sa.String(length=100000), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('botnine_token')
    )
    op.create_table('action_curls',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('chat_id', sa.UUID(), nullable=False),
    sa.Column('action_name', sa.Text(), nullable=False),
    sa.Column('curl_as_json', sa.Text(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['chat_id'], ['chat.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('message',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('chat_id', sa.UUID(), nullable=False),
    sa.Column('role', sa.Enum('user', 'assistant', name='role_enum'), nullable=False),
    sa.Column('content', sa.Text(), nullable=False),
    sa.Column('tool_name', sa.Text(), nullable=True),
    sa.Column('tool_use_id', sa.Text(), nullable=True),
    sa.Column('tool_input', sa.JSON(), nullable=True),
    sa.Column('tool_result', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['chat_id'], ['chat.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('message')
    op.drop_table('action_curls')
    op.drop_table('token')
    op.drop_table('chat')
    op.drop_table('user')
    # ### end Alembic commands ###
