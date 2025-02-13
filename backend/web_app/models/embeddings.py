from sqlmodel import Field, SQLModel


class Embedding(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    text: str = Field(index=True, nullable=False)
