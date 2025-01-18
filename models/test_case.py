from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional


class TestPriority(Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class TestType(Enum):
    FUNCTIONAL = "functional"
    INTEGRATION = "integration"
    EDGE_CASE = "edge_case"
    PERFORMANCE = "performance"


@dataclass
class TestStep:
    step_number: int
    description: str
    expected_result: str


@dataclass
class TestCase:
    id: str
    title: str
    description: str
    preconditions: List[str]
    steps: List[TestStep]
    priority: TestPriority
    test_type: TestType
    created_at: datetime = field(default_factory=datetime.now)
    jira_key: Optional[str] = None
    confluence_id: Optional[str] = None

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "preconditions": self.preconditions,
            "steps": [
                {
                    "step_number": step.step_number,
                    "description": step.description,
                    "expected_result": step.expected_result,
                }
                for step in self.steps
            ],
            "priority": self.priority.value,
            "test_type": self.test_type.value,
            "created_at": self.created_at.isoformat(),
            "jira_key": self.jira_key,
            "confluence_id": self.confluence_id,
        }
