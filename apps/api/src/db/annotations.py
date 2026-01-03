import uuid
from datetime import datetime
from typing import Annotated

from sqlalchemy import text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import mapped_column

str_50 = Annotated[str, 50]
str_255 = Annotated[str, 255]

uuidpk = Annotated[
    uuid.UUID,
    mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    ),
]


created_at = Annotated[
    datetime,
    mapped_column(server_default=text("TIMEZONE('utc', now())")),
]

expiries = Annotated[
    datetime,
    mapped_column(server_default=text("TIMEZONE('utc', now())")),
]
