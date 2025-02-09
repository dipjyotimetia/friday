import shutil
import tempfile
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from friday.api.schemas.api_test import ApiTestResponse
from friday.agents.api_agent import ApiTestGenerator

router = APIRouter()


@router.post("/testapi", response_model=ApiTestResponse)
async def test_api(
    base_url: str = Form(..., description="Base URL for API testing"),
    output: str = Form("api_test_report.md", description="Output file path"),
    spec_file: Optional[str] = Form(None, description="Path to OpenAPI spec file"),
    spec_upload: Optional[UploadFile] = File(
        None, description="OpenAPI spec file upload"
    ),
):
    """
    Run API tests using either a spec file path or uploaded spec file
    """
    try:
        # Validate required fields
        if not base_url:
            raise HTTPException(status_code=400, detail="base_url is required")

        if not spec_file and not spec_upload:
            raise HTTPException(
                status_code=400,
                detail="Either spec_file path or spec_upload file must be provided",
            )

        # Handle file upload
        if spec_upload:
            # Validate file type
            if not spec_upload.filename.endswith((".yaml", ".yml", ".json")):
                raise HTTPException(
                    status_code=400,
                    detail="Invalid file type. Must be .yaml, .yml or .json",
                )

            with tempfile.NamedTemporaryFile(delete=False, suffix=".yaml") as tmp_file:
                shutil.copyfileobj(spec_upload.file, tmp_file)
                spec_path = Path(tmp_file.name)
        else:
            spec_path = Path(spec_file)

        if not spec_path.exists():
            raise HTTPException(
                status_code=400, detail="OpenAPI specification file not found"
            )

        # Initialize generator
        generator = ApiTestGenerator(openapi_spec_path=str(spec_path))

        # Load and validate spec
        spec = await generator.load_spec()
        if not generator.validate_spec(spec):
            raise HTTPException(status_code=400, detail="Invalid OpenAPI specification")

        total_tests = 0
        paths_tested = 0

        # Test each endpoint
        for path, methods in spec["paths"].items():
            paths_tested += 1
            for method, details in methods.items():
                test_cases = await generator.create_test_cases(path, method, spec)
                total_tests += len(test_cases)
                await generator.execute_tests(test_cases, base_url=base_url.rstrip("/"))

        # Generate and save report
        report = await generator.generate_report()
        output_path = Path(output)
        output_path.write_text(report)

        # Handle file upload
        if spec_upload:
            spec_path.unlink()

        return {
            "message": f"Test report generated at {output}",
            "total_tests": total_tests,
            "paths_tested": paths_tested,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
