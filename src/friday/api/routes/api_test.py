import shutil
import tempfile
from pathlib import Path
from typing import Optional

import structlog
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from friday.agents.api_agents import ApiTestCreator, ApiTestExecutor
from friday.api.schemas.api_test import ApiTestRequest, ApiTestResponse
from friday.llm.llm import ModelProvider

router = APIRouter()


logger = structlog.get_logger(__name__)


async def get_api_test_request(
    base_url: str = Form(..., description="Base URL for API testing"),
    output: str = Form("api_test_report.md", description="Output file path"),
    spec_file: Optional[str] = Form(None, description="Path to OpenAPI spec file"),
    spec_upload: Optional[UploadFile] = File(
        None, description="OpenAPI spec file upload"
    ),
    provider: ModelProvider = Form("openai", description="LLM Provider"),
) -> ApiTestRequest:
    """
    Extract and validate API test request from form data.

    This function validates that either spec_file or spec_upload is provided.

    Args:
        base_url: Base URL for API testing
        output: Output file path for test results
        spec_file: Path to an existing OpenAPI spec file
        spec_upload: Uploaded OpenAPI spec file
        provider: LLM provider for test generation

    Returns:
        ApiTestRequest: Validated request object

    Raises:
        HTTPException: If neither spec_file nor spec_upload is provided
    """
    if not spec_file and not spec_upload:
        raise HTTPException(
            status_code=400, detail="Either spec_file or spec_upload must be provided"
        )
    return ApiTestRequest(
        base_url=base_url,
        output=output,
        spec_file=spec_file,
        spec_upload=spec_upload,
        provider=provider,
    )


@router.post("/testapi", response_model=ApiTestResponse)
async def test_api(request: ApiTestRequest = Depends(get_api_test_request)):
    """
    Generate and execute API tests using OpenAPI specification.

    This endpoint:
    1. Accepts an OpenAPI specification file
    2. Generates test cases for API endpoints
    3. Executes tests against the specified base URL
    4. Generates a comprehensive test report

    Args:
        request: API test request with specification and parameters

    Returns:
        ApiTestResponse: Summary of test execution

    Raises:
        HTTPException: For various error conditions during test generation/execution
    """
    try:
        spec_path = request.spec_file
        if request.spec_upload:
            # Create a temporary file for the uploaded spec
            fd, temp_path = tempfile.mkstemp(
                suffix=Path(request.spec_upload.filename).suffix
            )
            spec_path = temp_path
            with open(spec_path, "wb") as f:
                shutil.copyfileobj(request.spec_upload.file, f)

        paths_tested = 0
        total_tests = 0

        # Create a test creator to generate test cases
        async with ApiTestCreator(spec_path, provider=request.provider) as creator:
            spec = await creator.load_spec()

            if not creator.validate_spec(spec):
                raise HTTPException(
                    status_code=422, detail="Invalid OpenAPI specification"
                )

            test_cases_by_endpoint = {}

            # Generate test cases for each endpoint
            for path, path_details in spec["paths"].items():
                for method in path_details.keys():
                    # Skip parameters and other non-method keys
                    if method.lower() not in ["get", "post", "put", "delete", "patch"]:
                        continue

                    # Generate test cases for this endpoint/method
                    test_cases = await creator.create_test_cases(
                        path, method.upper(), spec
                    )
                    if test_cases:
                        test_cases_by_endpoint[(path, method.upper())] = test_cases
                        paths_tested += 1
                        total_tests += len(test_cases)

        # Use a test executor to run the tests and generate reports
        async with ApiTestExecutor(provider=request.provider) as executor:
            # Execute all the test cases
            for endpoint_method, test_cases in test_cases_by_endpoint.items():
                await executor.execute_tests(test_cases, request.base_url)

            # Generate a comprehensive report
            report = await executor.generate_report()

            # Save the report to the specified output file
            with open(request.output, "w") as f:
                f.write(report)

        # Clean up temporary file if created
        if request.spec_upload:
            Path(spec_path).unlink(missing_ok=True)

        # Return a summary of the test execution
        return ApiTestResponse(
            message=f"API tests executed successfully. Report saved to {request.output}",
            total_tests=total_tests,
            paths_tested=paths_tested,
        )

    except Exception as e:
        logger.error("API test failed", error=str(e))
        if request.spec_upload and spec_path != request.spec_file:
            Path(spec_path).unlink(missing_ok=True)
        raise HTTPException(status_code=500, detail=str(e))
