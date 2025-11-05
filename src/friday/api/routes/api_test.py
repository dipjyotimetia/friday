import logging
import shutil
import tempfile
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from friday.agents.api_agent import ApiTestGenerator
from friday.api.schemas.api_test import ApiTestRequest, ApiTestResponse
from friday.llm.llm import ModelProvider

router = APIRouter()

logger = logging.getLogger(__name__)


async def get_api_test_request(
    base_url: str = Form(..., description="Base URL for API testing"),
    output: str = Form("api_test_report.md", description="Output file path"),
    spec_file: Optional[str] = Form(None, description="Path to OpenAPI spec file"),
    spec_upload: Optional[UploadFile] = File(
        None, description="OpenAPI spec file upload"
    ),
    provider: ModelProvider = Form("openai", description="LLM Provider"),
) -> ApiTestRequest:
    return ApiTestRequest(
        base_url=base_url,
        output=output,
        spec_file=spec_file,
        spec_upload=spec_upload,
        provider=provider,
    )


@router.post("/testapi", response_model=ApiTestResponse)
async def test_api(api_test_request: ApiTestRequest = Depends(get_api_test_request)):
    """
    Run API tests using either a spec file path or uploaded spec file
    """
    try:
        # Validate required fields
        if not api_test_request.base_url:
            raise HTTPException(status_code=400, detail="base_url is required")

        if not api_test_request.spec_file and not api_test_request.spec_upload:
            raise HTTPException(
                status_code=400,
                detail="Either spec_file path or spec_upload file must be provided",
            )

        # Handle file upload
        if api_test_request.spec_upload:
            # Validate file type
            if not api_test_request.spec_upload.filename.endswith(
                (".yaml", ".yml", ".json")
            ):
                raise HTTPException(
                    status_code=400,
                    detail="Invalid file type. Must be .yaml, .yml or .json",
                )

            with tempfile.NamedTemporaryFile(delete=False, suffix=".yaml") as tmp_file:
                shutil.copyfileobj(api_test_request.spec_upload.file, tmp_file)
                spec_path = Path(tmp_file.name)
        else:
            spec_path = Path(api_test_request.spec_file)

        if not spec_path.exists():
            raise HTTPException(
                status_code=400, detail="OpenAPI specification file not found"
            )

        # Initialize generator
        generator = ApiTestGenerator(
            openapi_spec_path=str(spec_path), provider=api_test_request.provider
        )

        # Load and validate spec
        spec = await generator.load_spec()
        if not generator.validate_spec(spec):
            raise HTTPException(status_code=400, detail="Invalid OpenAPI specification")

        total_tests = 0
        paths_tested = 0
        test_results = []

        # Test each endpoint
        for path, methods in spec["paths"].items():
            paths_tested += 1
            for method, details in methods.items():
                # Skip non-HTTP methods like parameters, summary, etc.
                if method.lower() not in [
                    "get",
                    "post",
                    "put",
                    "delete",
                    "patch",
                    "head",
                    "options",
                ]:
                    continue

                test_cases = await generator.create_test_cases(path, method, spec)
                total_tests += len(test_cases)
                await generator.execute_tests(
                    test_cases, base_url=api_test_request.base_url.rstrip("/")
                )

        # Generate and save report
        report = await generator.generate_report()
        output_path = Path(api_test_request.output)
        output_path.write_text(report)

        # Calculate test statistics
        passed_tests = sum(
            1 for result in generator.test_results if result.get("status") == "PASS"
        )
        failed_tests = sum(
            1 for result in generator.test_results if result.get("status") == "FAIL"
        )
        error_tests = sum(
            1 for result in generator.test_results if result.get("status") == "ERROR"
        )

        # Handle file upload cleanup
        if api_test_request.spec_upload:
            spec_path.unlink()

        return {
            "success": True,
            "message": f"Test report generated at {api_test_request.output}",
            "total_tests": total_tests,
            "paths_tested": paths_tested,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "error_tests": error_tests,
            "success_rate": round(
                (passed_tests / total_tests * 100) if total_tests > 0 else 0, 2
            ),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in API test endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
