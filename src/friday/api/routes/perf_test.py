from typing import Optional

from fastapi import APIRouter, Form, UploadFile

from friday.llm.perf_agent import PerfTestGenerator

router = APIRouter()


@router.post("/perftest")
async def run_performance_test(
    spec_file: Optional[UploadFile] = None,
    curl_command: Optional[str] = Form(None),
    base_url: Optional[str] = Form(None),
    users: int = Form(10),
    duration: int = Form(30),
):
    generator = PerfTestGenerator(concurrent_users=users, duration=duration)

    if spec_file:
        spec_content = await spec_file.read()

        temp_path = f"/tmp/{spec_file.filename}"
        with open(temp_path, "wb") as f:
            f.write(spec_content)
        generator.spec_path = temp_path

    await generator.execute_load_test(base_url=base_url, curl_command=curl_command)
    return {"report": generator.generate_report()}
