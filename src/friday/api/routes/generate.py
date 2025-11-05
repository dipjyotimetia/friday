import logging

from fastapi import APIRouter, HTTPException

from friday.api.schemas.generate import GenerateRequest, GenerateResponse
from friday.connectors.confluence_client import ConfluenceConnector
from friday.connectors.github_client import GitHubConnector
from friday.connectors.jira_client import JiraConnector
from friday.services.test_generator import TestCaseGenerator
from friday.utils.helpers import save_test_cases_as_markdown

router = APIRouter()

logger = logging.getLogger(__name__)


@router.post("/generate", response_model=GenerateResponse)
async def generate_tests(request: GenerateRequest):
    if not request.jira_key and not request.gh_issue:
        raise HTTPException(
            status_code=400, detail="Either jira_key or gh_issue must be provided"
        )

    try:
        jira = JiraConnector()
        confluence = ConfluenceConnector()
        github = GitHubConnector()
        test_generator = TestCaseGenerator()

        if request.jira_key:
            issue_details = jira.get_issue_details(request.jira_key)
        else:
            issue_details = github.get_issue_details(
                request.gh_repo, int(request.gh_issue)
            )

        additional_context = ""
        if request.confluence_id:
            additional_context = confluence.get_page_content(request.confluence_id)

        test_generator.initialize_context(additional_context)

        test_cases = test_generator.generate_test_cases(
            requirement=issue_details["fields"]["description"]
        )

        save_test_cases_as_markdown(test_cases, request.output)
        return {
            "success": True,
            "message": f"Successfully generated test cases to {request.output}",
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating tests: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
