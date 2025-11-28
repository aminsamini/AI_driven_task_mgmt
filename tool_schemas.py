from pydantic import BaseModel

class SaveUserInfoArgs(BaseModel):
    user_id: str
    key: str
    value: str
