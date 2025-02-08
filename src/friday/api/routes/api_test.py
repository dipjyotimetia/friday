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

        async with ApiTestGenerator(openapi_spec_path=str(spec_path)) as generator:
            spec = await generator.load_spec()
            if not generator.validate_spec(spec):
                raise HTTPException(
                    status_code=400, detail="Invalid OpenAPI specification"
                )

            total_tests = 0
            paths_tested = 0

            for path, methods in spec["paths"].items():
                paths_tested += 1
                for method, details in methods.items():
                    test_cases = await generator.create_test_cases(path, method, spec)
                    total_tests += len(test_cases)
                    await generator.execute_tests(
                        test_cases, base_url=request.base_url.rstrip("/")
                    )

            report = await generator.generate_report()
            output_path = Path(request.output)
            output_path.write_text(report)

            return {
                "message": f"Test report generated at {request.output}",
                "total_tests": total_tests,
                "paths_tested": paths_tested,
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
