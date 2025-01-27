from openai import BaseModel


class VersionResponse(BaseModel):
    version: str
