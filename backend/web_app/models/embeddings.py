from sqlmodel import Field, SQLModel


class Embedding(SQLModel, table=True):
    id: int = Field(primary_key=True, nullable=False)
    text: str = Field(index=True, nullable=False)
