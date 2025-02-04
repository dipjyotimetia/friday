from pathlib import Path

from fastapi import APIRouter, HTTPException

from friday.api.schemas.api_test import ApiTestRequest, ApiTestResponse
from friday.llm.agent import ApiTestGenerator

router = APIRouter()


@router.post("/testapi", response_model=ApiTestResponse)
async def test_api(request: ApiTestRequest):
    try:
        spec_path = Path(request.spec_file)
        if not spec_path.exists():
            raise HTTPException(
                status_code=400, detail="OpenAPI specification file not found"
            )

        # Initialize the API test agent
        generator = ApiTestGenerator(openapi_spec_path=str(spec_path))

        # Load and validate spec
        spec = generator.load_spec()
        if not generator.validate_spec(spec):
            raise HTTPException(status_code=400, detail="Invalid OpenAPI specification")

        # Track statistics
        total_tests = 0
        paths_tested = 0

        # Test each endpoint
        for path, methods in spec["paths"].items():
            paths_tested += 1
            for method, details in methods.items():
                test_cases = generator.create_test_cases(path, method, spec)
                total_tests += len(test_cases)
                generator.execute_tests(
                    test_cases, base_url=request.base_url.rstrip("/")
                )

        # Generate and save test report
        report = generator.generate_report()
        output_path = Path(request.output)
        output_path.write_text(report)

        return {
            "message": f"Test report generated at {request.output}",
            "total_tests": total_tests,
            "paths_tested": paths_tested,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
