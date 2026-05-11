import uuid
from datetime import datetime
from typing_extensions import Annotated

from sqlalchemy import text, TIMESTAMP
from sqlalchemy.orm import DeclarativeBase, mapped_column

class Base(DeclarativeBase):
    repr_cols = tuple()

    def __repr__(self):
        cols = []
        for col in enumerate(self.__table__.columns.keys()):
            if col in self.repr_cols:
                value = getattr(self, col)
                if col == "text_content" and isinstance(value, str):
                    cols.append(f"{col}_length = {len(value)}")
                cols.append(f"{col} = {value}")
        
        return f"<{self.__class__.__name__} {", ".join(cols)}>"
    
int_primary_key = Annotated[int, mapped_column(primary_key=True, autoincrement=True)]
uuid_primary_key = Annotated[uuid.UUID, mapped_column(primary_key=True, default=uuid.uuid4)]

created_at = Annotated[datetime, mapped_column(server_default=text("TIMEZONE('utc', now())"))]
updated_at = Annotated[datetime, mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True)]