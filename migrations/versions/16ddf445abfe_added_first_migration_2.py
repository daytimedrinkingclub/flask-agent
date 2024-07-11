"""added first migration 2

Revision ID: 16ddf445abfe
Revises: 4099b0017225
Create Date: 2024-07-07 21:50:20.173609

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '16ddf445abfe'
down_revision = '4099b0017225'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('chatbot_actions', schema=None) as batch_op:
        batch_op.drop_column('is_active_on_bot9')

    with op.batch_alter_table('chatbots', schema=None) as batch_op:
        batch_op.alter_column('bot9_chatbot_id',
               existing_type=sa.UUID(),
               nullable=False)
        batch_op.alter_column('bot9_chatbot_name',
               existing_type=sa.VARCHAR(length=256),
               nullable=False)
        batch_op.drop_column('bot9_state')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('chatbots', schema=None) as batch_op:
        batch_op.add_column(sa.Column('bot9_state', sa.VARCHAR(length=256), autoincrement=False, nullable=True))
        batch_op.alter_column('bot9_chatbot_name',
               existing_type=sa.VARCHAR(length=256),
               nullable=True)
        batch_op.alter_column('bot9_chatbot_id',
               existing_type=sa.UUID(),
               nullable=True)

    with op.batch_alter_table('chatbot_actions', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_active_on_bot9', sa.BOOLEAN(), autoincrement=False, nullable=True))

    # ### end Alembic commands ###
