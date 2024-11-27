from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    password: str


class UserMe(BaseModel):
    email: str

    class Config:
        from_attributes = True
