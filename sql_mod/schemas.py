import sys
import logging
from pydantic import BaseModel

#logging.basicConfig(level=logging.DEBUG)
#logger = logging.getLogger(__name__)

class ItemBase(BaseModel):
    title: str
    description: str | None = None


class ItemCreate(ItemBase):
    pass


class Item(ItemBase):
    id: int
    owner_id: int

    class Config:
        from_attributes = True


class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    is_active: bool
    items: list[Item] = []

    class Config:
        from_attributes = True


class project(BaseModel):
    project_id: str | None = None
    description: str
    name: str   

    class Config:
        from_attributes = True

class Extension(BaseModel):
    project_id: int
    id: int
    topic_type: str
    topic_status: str
    topic_label: str
    snippet_type: str
    priority: str
    stage: str
    users: list[str] = []
    project_actions: list[str] = []
    topic_actions: list[str] = []
    comment_actions: list[str] = []
    view_setup: list[str] = []

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None
    scopes: list[str] = []

class UserInDB(BaseModel):
    hashed_password: str
    email: str
    username: str
    disabled: bool
    uuid: str

class InitiateUploadResponse(BaseModel):
    upload_ui_url: str
    expires_in: int
    max_size_in_bytes: int

class CompleteUploadResponse(BaseModel):
    uploadId: str
    status: str
    fileName: str
    fileSize: int
    metadata: dict


if __name__ == "__main__":
    sys.stdout = open('stdout.log', 'w')
    sys.stderr = open('stderr.log', 'w')

