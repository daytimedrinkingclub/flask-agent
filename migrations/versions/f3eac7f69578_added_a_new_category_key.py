"""added a new category key

Revision ID: f3eac7f69578
Revises: 52ea60ba3eb0
Create Date: 2024-07-07 13:07:04.230723

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f3eac7f69578'
down_revision = '52ea60ba3eb0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('chatbot_instructions', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_category', sa.Boolean(), nullable=True))
        batch_op.drop_index('ix_chatbot_instructions_bot9_instruction_category_id')
        batch_op.create_index(batch_op.f('ix_chatbot_instructions_bot9_instruction_category_id'), ['bot9_instruction_category_id'], unique=False)
        batch_op.drop_index('ix_chatbot_instructions_bot9_instruction_id')
        batch_op.create_index(batch_op.f('ix_chatbot_instructions_bot9_instruction_id'), ['bot9_instruction_id'], unique=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('chatbot_instructions', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_chatbot_instructions_bot9_instruction_id'))
        batch_op.create_index('ix_chatbot_instructions_bot9_instruction_id', ['bot9_instruction_id'], unique=True)
        batch_op.drop_index(batch_op.f('ix_chatbot_instructions_bot9_instruction_category_id'))
        batch_op.create_index('ix_chatbot_instructions_bot9_instruction_category_id', ['bot9_instruction_category_id'], unique=True)
        batch_op.drop_column('is_category')

    # ### end Alembic commands ###
