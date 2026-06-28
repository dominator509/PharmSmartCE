"""Initial data model.

# reversible: yes
"""

from alembic import op
from app.repositories import models as _models  # noqa: F401
from app.repositories.db import Base

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    Base.metadata.create_all(bind=op.get_bind())


def downgrade() -> None:
    Base.metadata.drop_all(bind=op.get_bind())
