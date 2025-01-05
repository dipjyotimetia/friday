import uuid
from typing import Dict, List

from friday.models.test_case import TestCase, TestPriority, TestStep, TestType


def generate_test_id(prefix: str = "TC") -> str:
    """Generate a unique test case ID"""
    unique_id = str(uuid.uuid4())[:8]
    return f"{prefix}-{unique_id}"


def parse_llm_response(response: str) -> List[Dict]:
    """Parse LLM generated test cases into structured format"""
    test_cases = []
    current_test = {}

    for line in response.split("\n"):
        line = line.strip()
        if line.startswith("Test ID:"):
            if current_test:
                test_cases.append(current_test)
            current_test = {"id": line.split("Test ID:")[1].strip()}
        elif line.startswith("Title:"):
            current_test["title"] = line.split("Title:")[1].strip()
        elif line.startswith("Preconditions:"):
            current_test["preconditions"] = [
                p.strip() for p in line.split("Preconditions:")[1].strip().split(",")
            ]
        elif line.startswith("Test Type:"):
            test_type = line.split("Test Type:")[1].strip().lower()
            current_test["test_type"] = test_type
        elif line.startswith("Priority:"):
            priority = line.split("Priority:")[1].strip().lower()
            current_test["priority"] = priority

    if current_test:
        test_cases.append(current_test)

    return test_cases


def create_test_case_from_dict(data: Dict) -> TestCase:
    """Create TestCase object from dictionary"""
    return TestCase(
        id=data.get("id", generate_test_id()),
        title=data["title"],
        description=data.get("description", ""),
        preconditions=data.get("preconditions", []),
        steps=[TestStep(**step) for step in data.get("steps", [])],
        priority=TestPriority(data.get("priority", "medium")),
        test_type=TestType(data.get("test_type", "functional")),
        jira_key=data.get("jira_key"),
        confluence_id=data.get("confluence_id"),
    )


def validate_test_case(test_case: TestCase) -> List[str]:
    """Validate test case data"""
    errors = []

    if not test_case.title:
        errors.append("Test case title is required")
    if not test_case.steps:
        errors.append("Test case must have at least one step")
    if len(test_case.title) > 200:
        errors.append("Test case title exceeds maximum length of 200 characters")

    return errors
