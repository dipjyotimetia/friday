"""
Browser Testing API Routes

This module provides FastAPI routes for browser testing functionality.
It supports YAML file uploads, test execution, and real-time monitoring.
"""

import asyncio
import json
import logging
import uuid
from typing import Dict, Optional

from fastapi import APIRouter, BackgroundTasks, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse

from friday.api.schemas.browser_test import (
    BrowserTestExecutionRequest,
    BrowserTestExecutionResponse,
    BrowserTestHealthResponse,
    BrowserTestLogEntry,
    BrowserTestWebSocketMessage,
    YamlUploadRequest,
    YamlUploadResponse,
)
from friday.services.browser_agent import BrowserTestingAgent, execute_yaml_content
from friday.services.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/browser-test", tags=["browser-test"])

# In-memory storage for uploaded files and execution results
uploaded_files: Dict[str, str] = {}
execution_results: Dict[str, dict] = {}
active_websockets: Dict[str, WebSocket] = {}


@router.post("/yaml/upload", response_model=YamlUploadResponse)
async def upload_yaml_file(request: YamlUploadRequest):
    """
    Upload a YAML test file for browser testing.
    
    Args:
        request: YAML upload request with filename and content
        
    Returns:
        Upload response with file ID and parsed suite
    """
    try:
        logger.info(f"Uploading YAML file: {request.filename}")
        
        # Generate unique file ID
        file_id = str(uuid.uuid4())
        
        # Store file content
        uploaded_files[file_id] = request.content
        
        # Parse YAML to validate
        agent = BrowserTestingAgent()
        suite = await agent.load_yaml_suite(request.content)
        
        response = YamlUploadResponse(
            message=f"Successfully uploaded {request.filename}",
            file_id=file_id,
            parsed_suite=suite,
        )
        
        logger.info(f"YAML file uploaded successfully: {file_id}")
        return response
        
    except Exception as e:
        logger.error(f"Failed to upload YAML file: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid YAML file: {e}")


@router.post("/yaml/execute", response_model=BrowserTestExecutionResponse)
async def execute_yaml_test(
    request: BrowserTestExecutionRequest,
    background_tasks: BackgroundTasks,
):
    """
    Execute browser tests from uploaded YAML file or direct test suite.
    
    Args:
        request: Test execution request
        background_tasks: FastAPI background tasks
        
    Returns:
        Execution response with execution ID
    """
    try:
        logger.info(f"Starting browser test execution")
        
        # Generate execution ID
        execution_id = str(uuid.uuid4())
        
        # Get YAML content
        yaml_content = None
        if request.file_id:
            if request.file_id not in uploaded_files:
                raise HTTPException(status_code=404, detail="File not found")
            yaml_content = uploaded_files[request.file_id]
        elif request.test_suite:
            # Convert test suite back to YAML
            import yaml
            suite_dict = request.test_suite.model_dump()
            yaml_content = yaml.dump(suite_dict, default_flow_style=False)
        else:
            raise HTTPException(
                status_code=400, 
                detail="Either file_id or test_suite must be provided"
            )
        
        # Initialize execution result
        execution_results[execution_id] = {
            "status": "running",
            "started_at": None,
            "completed_at": None,
            "report": None,
            "error": None,
        }
        
        # Execute tests in background
        background_tasks.add_task(
            _execute_browser_tests,
            execution_id,
            yaml_content,
            request.provider,
            request.headless,
        )
        
        response = BrowserTestExecutionResponse(
            message="Browser test execution started",
            execution_id=execution_id,
            status="running",
        )
        
        logger.info(f"Browser test execution started: {execution_id}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start browser test execution: {e}")
        raise HTTPException(status_code=500, detail=f"Execution failed: {e}")


@router.get("/execution/{execution_id}")
async def get_execution_status(execution_id: str):
    """
    Get the status of a browser test execution.
    
    Args:
        execution_id: Unique execution identifier
        
    Returns:
        Execution status and results
    """
    if execution_id not in execution_results:
        raise HTTPException(status_code=404, detail="Execution not found")
    
    result = execution_results[execution_id]
    return JSONResponse(content=result)


@router.post("/report/{execution_id}")
async def generate_report(execution_id: str, format: str = "json"):
    """
    Generate a formatted report for completed test execution.
    
    Args:
        execution_id: Unique execution identifier
        format: Report format (json, markdown, html)
        
    Returns:
        Formatted test report
    """
    if execution_id not in execution_results:
        raise HTTPException(status_code=404, detail="Execution not found")
    
    result = execution_results[execution_id]
    
    if result["status"] != "completed":
        raise HTTPException(
            status_code=400, 
            detail="Execution not completed"
        )
    
    if not result["report"]:
        raise HTTPException(status_code=404, detail="Report not found")
    
    report = result["report"]
    
    if format == "json":
        return JSONResponse(content=report)
    elif format == "markdown":
        markdown_report = _generate_markdown_report(report)
        return JSONResponse(content={"report": markdown_report})
    elif format == "html":
        html_report = _generate_html_report(report)
        return JSONResponse(content={"report": html_report})
    else:
        raise HTTPException(
            status_code=400, 
            detail="Unsupported format. Use 'json', 'markdown', or 'html'"
        )


@router.get("/health", response_model=BrowserTestHealthResponse)
async def health_check():
    """
    Check the health of browser testing service.
    
    Returns:
        Health check response
    """
    try:
        agent = BrowserTestingAgent()
        health_data = await agent.health_check()
        
        return BrowserTestHealthResponse(**health_data)
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {e}")


@router.websocket("/ws/{execution_id}")
async def websocket_endpoint(websocket: WebSocket, execution_id: str):
    """
    WebSocket endpoint for real-time test execution monitoring.
    
    Args:
        websocket: WebSocket connection
        execution_id: Execution ID to monitor
    """
    await websocket.accept()
    active_websockets[execution_id] = websocket
    
    try:
        logger.info(f"WebSocket connected for execution: {execution_id}")
        
        # Send initial status
        if execution_id in execution_results:
            status_msg = BrowserTestWebSocketMessage(
                type="status_update",
                execution_id=execution_id,
                data=execution_results[execution_id],
            )
            await websocket.send_json(status_msg.model_dump())
        
        # Keep connection alive and send updates
        while True:
            try:
                # Wait for messages or send heartbeat
                await asyncio.sleep(1)
                
                # Send heartbeat
                heartbeat_msg = BrowserTestWebSocketMessage(
                    type="heartbeat",
                    execution_id=execution_id,
                    data={"timestamp": str(asyncio.get_event_loop().time())},
                )
                await websocket.send_json(heartbeat_msg.model_dump())
                
            except WebSocketDisconnect:
                break
                
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for execution: {execution_id}")
    except Exception as e:
        logger.error(f"WebSocket error for execution {execution_id}: {e}")
    finally:
        # Clean up
        if execution_id in active_websockets:
            del active_websockets[execution_id]


async def _execute_browser_tests(
    execution_id: str,
    yaml_content: str,
    provider: str,
    headless: bool,
):
    """
    Execute browser tests in background.
    
    Args:
        execution_id: Unique execution identifier
        yaml_content: YAML test content
        provider: LLM provider
        headless: Whether to run headless
    """
    from datetime import datetime
    
    try:
        logger.info(f"Starting background execution: {execution_id}")
        
        # Update status
        execution_results[execution_id]["status"] = "running"
        execution_results[execution_id]["started_at"] = datetime.now().isoformat()
        
        # Send WebSocket update
        await _send_websocket_update(execution_id, "execution_started", {
            "message": "Browser test execution started"
        })
        
        # Execute tests
        report = await execute_yaml_content(
            yaml_content=yaml_content,
            provider=provider,
            headless=headless,
        )
        
        # Update results
        execution_results[execution_id]["status"] = "completed"
        execution_results[execution_id]["completed_at"] = datetime.now().isoformat()
        execution_results[execution_id]["report"] = report.model_dump()
        
        # Send WebSocket update
        await _send_websocket_update(execution_id, "execution_completed", {
            "message": "Browser test execution completed",
            "report": report.model_dump(),
        })
        
        logger.info(f"Background execution completed: {execution_id}")
        
    except Exception as e:
        logger.error(f"Background execution failed: {execution_id} - {e}")
        
        # Update results with error
        execution_results[execution_id]["status"] = "failed"
        execution_results[execution_id]["completed_at"] = datetime.now().isoformat()
        execution_results[execution_id]["error"] = str(e)
        
        # Send WebSocket update
        await _send_websocket_update(execution_id, "execution_failed", {
            "message": "Browser test execution failed",
            "error": str(e),
        })


async def _send_websocket_update(execution_id: str, message_type: str, data: dict):
    """
    Send WebSocket update to connected clients.
    
    Args:
        execution_id: Execution ID
        message_type: Type of message
        data: Message data
    """
    if execution_id in active_websockets:
        try:
            message = BrowserTestWebSocketMessage(
                type=message_type,
                execution_id=execution_id,
                data=data,
            )
            await active_websockets[execution_id].send_json(message.model_dump())
            
        except Exception as e:
            logger.error(f"Failed to send WebSocket update: {e}")


def _generate_markdown_report(report: dict) -> str:
    """
    Generate markdown report from test results.
    
    Args:
        report: Test report dictionary
        
    Returns:
        Markdown formatted report
    """
    md = []
    md.append(f"# Browser Test Report: {report['suite_name']}")
    md.append("")
    md.append("## Summary")
    md.append(f"- **Total Tests**: {report['total_tests']}")
    md.append(f"- **Passed**: {report['passed_tests']}")
    md.append(f"- **Failed**: {report['failed_tests']}")
    md.append(f"- **Success Rate**: {report['success_rate']:.1f}%")
    md.append(f"- **Execution Time**: {report['execution_time']:.2f}s")
    md.append("")
    
    md.append("## Test Results")
    for result in report['results']:
        status_emoji = "✅" if result['success'] else "❌"
        md.append(f"### {status_emoji} {result['scenario_name']}")
        md.append(f"- **Status**: {result['status']}")
        md.append(f"- **Execution Time**: {result['execution_time']:.2f}s")
        
        if result['error_message']:
            md.append(f"- **Error**: {result['error_message']}")
        
        if result['screenshot_path']:
            md.append(f"- **Screenshot**: {result['screenshot_path']}")
        
        md.append("")
    
    return "\n".join(md)


def _generate_html_report(report: dict) -> str:
    """
    Generate HTML report from test results.
    
    Args:
        report: Test report dictionary
        
    Returns:
        HTML formatted report
    """
    html = []
    html.append(f"<h1>Browser Test Report: {report['suite_name']}</h1>")
    html.append("<h2>Summary</h2>")
    html.append("<ul>")
    html.append(f"<li><strong>Total Tests</strong>: {report['total_tests']}</li>")
    html.append(f"<li><strong>Passed</strong>: {report['passed_tests']}</li>")
    html.append(f"<li><strong>Failed</strong>: {report['failed_tests']}</li>")
    html.append(f"<li><strong>Success Rate</strong>: {report['success_rate']:.1f}%</li>")
    html.append(f"<li><strong>Execution Time</strong>: {report['execution_time']:.2f}s</li>")
    html.append("</ul>")
    
    html.append("<h2>Test Results</h2>")
    for result in report['results']:
        status_class = "success" if result['success'] else "failure"
        status_symbol = "✅" if result['success'] else "❌"
        
        html.append(f"<div class='test-result {status_class}'>")
        html.append(f"<h3>{status_symbol} {result['scenario_name']}</h3>")
        html.append(f"<p><strong>Status</strong>: {result['status']}</p>")
        html.append(f"<p><strong>Execution Time</strong>: {result['execution_time']:.2f}s</p>")
        
        if result['error_message']:
            html.append(f"<p><strong>Error</strong>: {result['error_message']}</p>")
        
        if result['screenshot_path']:
            html.append(f"<p><strong>Screenshot</strong>: <a href='{result['screenshot_path']}'>View</a></p>")
        
        html.append("</div>")
    
    return "\n".join(html)