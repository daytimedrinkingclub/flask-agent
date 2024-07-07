"""Add indexes to ChatbotInstruction

Revision ID: 52ea60ba3eb0
Revises: 764822683729
Create Date: 2024-07-07 12:51:25.937261

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '52ea60ba3eb0'
down_revision = '764822683729'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('chatbot_instructions', schema=None) as batch_op:
        batch_op.drop_constraint('chatbot_instructions_bot9_instruction_category_id_key', type_='unique')
        batch_op.drop_constraint('chatbot_instructions_bot9_instruction_id_key', type_='unique')
        batch_op.create_index('idx_chatbot_instruction', ['bot9_chatbot_id', 'bot9_instruction_id'], unique=False)
        batch_op.create_index('idx_chatbot_instruction_category', ['bot9_chatbot_id', 'bot9_instruction_category_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_chatbot_instructions_bot9_chatbot_id'), ['bot9_chatbot_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_chatbot_instructions_bot9_instruction_category_id'), ['bot9_instruction_category_id'], unique=True)
        batch_op.create_index(batch_op.f('ix_chatbot_instructions_bot9_instruction_id'), ['bot9_instruction_id'], unique=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('chatbot_instructions', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_chatbot_instructions_bot9_instruction_id'))
        batch_op.drop_index(batch_op.f('ix_chatbot_instructions_bot9_instruction_category_id'))
        batch_op.drop_index(batch_op.f('ix_chatbot_instructions_bot9_chatbot_id'))
        batch_op.drop_index('idx_chatbot_instruction_category')
        batch_op.drop_index('idx_chatbot_instruction')
        batch_op.create_unique_constraint('chatbot_instructions_bot9_instruction_id_key', ['bot9_instruction_id'])
        batch_op.create_unique_constraint('chatbot_instructions_bot9_instruction_category_id_key', ['bot9_instruction_category_id'])

    # ### end Alembic commands ###
