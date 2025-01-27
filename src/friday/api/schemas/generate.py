from typing import Optional

from openai import BaseModel


class GenerateRequest(BaseModel):
    jira_key: Optional[str] = None
    gh_issue: Optional[str] = None
    gh_repo: Optional[str] = None
    confluence_id: Optional[str] = None
    template: str = "test_case"
    output: str = "test_cases.md"


class GenerateResponse(BaseModel):
    message: str
