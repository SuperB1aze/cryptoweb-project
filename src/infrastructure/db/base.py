from sqlalchemy.orm import DeclarativeBase

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