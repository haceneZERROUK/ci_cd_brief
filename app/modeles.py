from typing import Optional
from datetime import datetime
from sqlmodel import Field, SQLModel, Column, String




class Users(SQLModel, table=True):      # la banque
    id_cinema : Optional[int] = Field(default=None, primary_key=True, index=True)
    cinema_name : str = Field(sa_column=Column(String(255), unique=True))
    email: str = Field(sa_column=Column(String(255), unique=True))
    hashed_password: str = Field(sa_column=Column(String(255)))
    role: str = Field(sa_column=Column(String(50)), default="cinema")

