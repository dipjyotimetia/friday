import asyncio
from typing import List, Dict, Any

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse

from friday.api.schemas.browser_test import (
    BrowserTestRequest,
    BrowserTestResponse,
    MultipleBrowserTestRequest,
    MultipleBrowserTestResponse,
    BrowserTestReportRequest,
    BrowserTestReportResponse,
    BrowserTestResult
)
from friday.services.browser_agent import BrowserTestingAgent
from friday.services.logger import get_logger
from friday.llm.llm import ModelProvider

logger = get_logger(__name__)

router = APIRouter(prefix="/browser-test", tags=["browser-testing"])


@router.post("/single", response_model=BrowserTestResponse)
async def run_single_browser_test(request: BrowserTestRequest):
    """
    Run a single browser test using the browser-use agent
    """
    try:
        logger.info(f"Starting single browser test for URL: {request.url}")
        
        # Initialize browser testing agent
        agent = BrowserTestingAgent(provider=ModelProvider.OPENAI)
        
        # Run the browser test
        result = await agent.run_browser_test(
            requirement=request.requirement,
            url=str(request.url),
            test_type=request.test_type,
            context=request.context,
            headless=request.headless,
            take_screenshots=request.take_screenshots
        )
        
        # Convert result to BrowserTestResult model
        test_result = BrowserTestResult(**result)
        
        return BrowserTestResponse(
            success=True,
            message="Browser test completed successfully",
            data=test_result
        )
        
    except Exception as e:
        logger.error(f"Error running browser test: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to run browser test: {str(e)}"
        )


@router.post("/multiple", response_model=MultipleBrowserTestResponse)
async def run_multiple_browser_tests(request: MultipleBrowserTestRequest):
    """
    Run multiple browser tests in sequence
    """
    try:
        logger.info(f"Starting multiple browser tests with {len(request.test_cases)} test cases")
        
        # Initialize browser testing agent
        agent = BrowserTestingAgent(provider=ModelProvider.OPENAI)
        
        # Convert test cases to dict format
        test_cases = []
        for test_case in request.test_cases:
            test_cases.append({
                "requirement": test_case.requirement,
                "url": str(test_case.url),
                "test_type": test_case.test_type,
                "context": test_case.context,
                "take_screenshots": test_case.take_screenshots
            })
        
        # Run multiple browser tests
        results = await agent.run_multiple_tests(
            test_cases=test_cases,
            headless=request.headless
        )
        
        # Convert results to BrowserTestResult models
        test_results = [BrowserTestResult(**result) for result in results]
        
        # Generate test report
        report = agent.generate_test_report(results)
        
        # Create summary
        total_tests = len(results)
        passed_tests = sum(1 for r in results if r.get("success", False))
        failed_tests = total_tests - passed_tests
        
        summary = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        }
        
        return MultipleBrowserTestResponse(
            success=True,
            message=f"Multiple browser tests completed. {passed_tests}/{total_tests} tests passed",
            data=test_results,
            report=report,
            summary=summary
        )
        
    except Exception as e:
        logger.error(f"Error running multiple browser tests: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to run multiple browser tests: {str(e)}"
        )


@router.post("/report", response_model=BrowserTestReportResponse)
async def generate_browser_test_report(request: BrowserTestReportRequest):
    """
    Generate a test report from browser test results
    """
    try:
        logger.info(f"Generating test report for {len(request.results)} test results")
        
        # Initialize browser testing agent
        agent = BrowserTestingAgent(provider=ModelProvider.OPENAI)
        
        # Convert results to dict format for report generation
        results_dict = []
        for result in request.results:
            results_dict.append(result.dict())
        
        # Generate test report
        report = agent.generate_test_report(results_dict)
        
        # Create summary
        total_tests = len(request.results)
        passed_tests = sum(1 for r in request.results if r.success)
        failed_tests = total_tests - passed_tests
        
        summary = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        }
        
        return BrowserTestReportResponse(
            success=True,
            message="Test report generated successfully",
            report=report,
            summary=summary
        )
        
    except Exception as e:
        logger.error(f"Error generating test report: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate test report: {str(e)}"
        )


@router.get("/health")
async def browser_test_health():
    """
    Health check endpoint for browser testing service
    """
    try:
        # Basic health check - try to initialize the agent
        agent = BrowserTestingAgent(provider=ModelProvider.OPENAI)
        
        return JSONResponse(
            status_code=200,
            content={
                "status": "healthy",
                "message": "Browser testing service is operational",
                "service": "browser-testing",
                "version": "1.0.0"
            }
        )
    except Exception as e:
        logger.error(f"Browser testing service health check failed: {str(e)}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "message": f"Browser testing service is not operational: {str(e)}",
                "service": "browser-testing",
                "version": "1.0.0"
            }
        )