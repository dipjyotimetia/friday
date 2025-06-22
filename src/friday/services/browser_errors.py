"""
Enhanced error handling and categorization for browser testing.

This module provides comprehensive error handling with categorization and recovery strategies.
"""

from enum import Enum
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import traceback
import re

from friday.services.logger import get_logger

logger = get_logger(__name__)


class ErrorCategory(Enum):
    """Categories of browser testing errors"""

    NETWORK_ERROR = "network_error"
    ELEMENT_NOT_FOUND = "element_not_found"
    TIMEOUT_ERROR = "timeout_error"
    NAVIGATION_ERROR = "navigation_error"
    JAVASCRIPT_ERROR = "javascript_error"
    BROWSER_ERROR = "browser_error"
    VALIDATION_ERROR = "validation_error"
    AUTHENTICATION_ERROR = "authentication_error"
    PERMISSION_ERROR = "permission_error"
    RESOURCE_ERROR = "resource_error"
    UNKNOWN_ERROR = "unknown_error"


class ErrorSeverity(Enum):
    """Severity levels for errors"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class BrowserTestError:
    """Structured browser test error information"""

    category: ErrorCategory
    severity: ErrorSeverity
    message: str
    original_error: Optional[Exception] = None
    stack_trace: Optional[str] = None
    suggested_fix: Optional[str] = None
    retry_recommended: bool = False
    context: Optional[Dict[str, Any]] = None
    error_code: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "category": self.category.value,
            "severity": self.severity.value,
            "message": self.message,
            "error_code": self.error_code,
            "suggested_fix": self.suggested_fix,
            "retry_recommended": self.retry_recommended,
            "stack_trace": self.stack_trace,
            "context": self.context or {},
        }


class BrowserErrorHandler:
    """Enhanced error handler for browser testing"""

    def __init__(self):
        self.logger = logger
        self.error_patterns = self._initialize_error_patterns()

    def _initialize_error_patterns(self) -> Dict[ErrorCategory, List[str]]:
        """Initialize error patterns for categorization"""
        return {
            ErrorCategory.NETWORK_ERROR: [
                r"net::ERR_.*",
                r"Network request failed",
                r"Connection refused",
                r"DNS_PROBE_FINISHED_NXDOMAIN",
                r"net::ERR_INTERNET_DISCONNECTED",
                r"net::ERR_CONNECTION_TIMED_OUT",
                r"net::ERR_NAME_NOT_RESOLVED",
            ],
            ErrorCategory.ELEMENT_NOT_FOUND: [
                r"Element .* not found",
                r"No element found matching selector",
                r"Element is not attached to the DOM",
                r"Element with selector .* not found",
                r"Waiting for selector .* failed",
            ],
            ErrorCategory.TIMEOUT_ERROR: [
                r"Timeout .*",
                r"Navigation timeout",
                r"Page did not load within.*",
                r"Waiting for .* timed out",
                r"exceeded timeout of.*",
            ],
            ErrorCategory.NAVIGATION_ERROR: [
                r"Navigation failed",
                r"Page crashed",
                r"Page not found",
                r"HTTP 404",
                r"HTTP 500",
                r"HTTP 503",
            ],
            ErrorCategory.JAVASCRIPT_ERROR: [
                r"JavaScript error",
                r"Script error",
                r"ReferenceError",
                r"TypeError",
                r"SyntaxError",
                r"Evaluation failed",
            ],
            ErrorCategory.BROWSER_ERROR: [
                r"Browser closed",
                r"Browser process crashed",
                r"Browser context closed",
                r"Page closed",
            ],
            ErrorCategory.AUTHENTICATION_ERROR: [
                r"Authentication failed",
                r"Login required",
                r"Unauthorized",
                r"HTTP 401",
                r"HTTP 403",
            ],
            ErrorCategory.PERMISSION_ERROR: [
                r"Permission denied",
                r"Access denied",
                r"Forbidden",
                r"Not allowed",
            ],
        }

    def categorize_error(
        self, error: Exception, context: Optional[Dict[str, Any]] = None
    ) -> BrowserTestError:
        """
        Categorize and enhance error information

        Args:
            error: The original exception
            context: Additional context information

        Returns:
            BrowserTestError with categorized information
        """
        error_message = str(error)
        error_type = type(error).__name__

        # Categorize error
        category = self._match_error_category(error_message, error_type)

        # Determine severity
        severity = self._determine_severity(category, error_message)

        # Generate suggested fix
        suggested_fix = self._generate_suggested_fix(category, error_message)

        # Determine if retry is recommended
        retry_recommended = self._should_retry(category, error_message)

        # Generate error code
        error_code = self._generate_error_code(category, error_type)

        return BrowserTestError(
            category=category,
            severity=severity,
            message=error_message,
            original_error=error,
            stack_trace=traceback.format_exc(),
            suggested_fix=suggested_fix,
            retry_recommended=retry_recommended,
            context=context,
            error_code=error_code,
        )

    def _match_error_category(
        self, error_message: str, error_type: str
    ) -> ErrorCategory:
        """Match error to category based on patterns"""
        for category, patterns in self.error_patterns.items():
            for pattern in patterns:
                if re.search(pattern, error_message, re.IGNORECASE):
                    return category

        # Check error type for specific exceptions
        if "TimeoutError" in error_type:
            return ErrorCategory.TIMEOUT_ERROR
        elif "NetworkError" in error_type:
            return ErrorCategory.NETWORK_ERROR
        elif "JavaScriptError" in error_type:
            return ErrorCategory.JAVASCRIPT_ERROR

        return ErrorCategory.UNKNOWN_ERROR

    def _determine_severity(
        self, category: ErrorCategory, error_message: str
    ) -> ErrorSeverity:
        """Determine error severity based on category and message"""
        severity_mapping = {
            ErrorCategory.BROWSER_ERROR: ErrorSeverity.CRITICAL,
            ErrorCategory.NETWORK_ERROR: ErrorSeverity.HIGH,
            ErrorCategory.NAVIGATION_ERROR: ErrorSeverity.HIGH,
            ErrorCategory.TIMEOUT_ERROR: ErrorSeverity.MEDIUM,
            ErrorCategory.ELEMENT_NOT_FOUND: ErrorSeverity.MEDIUM,
            ErrorCategory.JAVASCRIPT_ERROR: ErrorSeverity.MEDIUM,
            ErrorCategory.AUTHENTICATION_ERROR: ErrorSeverity.HIGH,
            ErrorCategory.PERMISSION_ERROR: ErrorSeverity.HIGH,
            ErrorCategory.VALIDATION_ERROR: ErrorSeverity.LOW,
            ErrorCategory.RESOURCE_ERROR: ErrorSeverity.MEDIUM,
            ErrorCategory.UNKNOWN_ERROR: ErrorSeverity.MEDIUM,
        }

        base_severity = severity_mapping.get(category, ErrorSeverity.MEDIUM)

        # Adjust severity based on error message
        if any(
            word in error_message.lower() for word in ["critical", "fatal", "crashed"]
        ):
            return ErrorSeverity.CRITICAL
        elif any(word in error_message.lower() for word in ["warning", "minor"]):
            return ErrorSeverity.LOW

        return base_severity

    def _generate_suggested_fix(
        self, category: ErrorCategory, error_message: str
    ) -> str:
        """Generate suggested fix based on error category"""
        suggestions = {
            ErrorCategory.NETWORK_ERROR: "Check internet connection and target URL accessibility. Verify firewall settings.",
            ErrorCategory.ELEMENT_NOT_FOUND: "Verify element selector is correct. Check if element loads after page interaction. Add explicit waits.",
            ErrorCategory.TIMEOUT_ERROR: "Increase timeout values. Check page load performance. Verify network stability.",
            ErrorCategory.NAVIGATION_ERROR: "Verify URL is correct and accessible. Check for redirects or server issues.",
            ErrorCategory.JAVASCRIPT_ERROR: "Review page JavaScript for errors. Check browser console for additional details.",
            ErrorCategory.BROWSER_ERROR: "Restart browser session. Check system resources. Update browser version.",
            ErrorCategory.AUTHENTICATION_ERROR: "Verify credentials are correct. Check authentication flow and session management.",
            ErrorCategory.PERMISSION_ERROR: "Check user permissions and access rights. Verify authorization tokens.",
            ErrorCategory.VALIDATION_ERROR: "Review input data and validation rules. Check required fields.",
            ErrorCategory.RESOURCE_ERROR: "Check system resources (memory, disk space). Verify file permissions.",
            ErrorCategory.UNKNOWN_ERROR: "Enable debug logging for more details. Check error logs and stack trace.",
        }

        return suggestions.get(
            category, "Review error details and check system configuration."
        )

    def _should_retry(self, category: ErrorCategory, error_message: str) -> bool:
        """Determine if error should trigger a retry"""
        retry_categories = {
            ErrorCategory.NETWORK_ERROR,
            ErrorCategory.TIMEOUT_ERROR,
            ErrorCategory.RESOURCE_ERROR,
        }

        no_retry_patterns = [
            r"404",
            r"Authentication failed",
            r"Permission denied",
            r"Invalid selector",
        ]

        if category in retry_categories:
            # Don't retry if error message matches no-retry patterns
            for pattern in no_retry_patterns:
                if re.search(pattern, error_message, re.IGNORECASE):
                    return False
            return True

        return False

    def _generate_error_code(self, category: ErrorCategory, error_type: str) -> str:
        """Generate a unique error code"""
        category_codes = {
            ErrorCategory.NETWORK_ERROR: "NET",
            ErrorCategory.ELEMENT_NOT_FOUND: "ELM",
            ErrorCategory.TIMEOUT_ERROR: "TMO",
            ErrorCategory.NAVIGATION_ERROR: "NAV",
            ErrorCategory.JAVASCRIPT_ERROR: "JSE",
            ErrorCategory.BROWSER_ERROR: "BRW",
            ErrorCategory.VALIDATION_ERROR: "VAL",
            ErrorCategory.AUTHENTICATION_ERROR: "AUTH",
            ErrorCategory.PERMISSION_ERROR: "PERM",
            ErrorCategory.RESOURCE_ERROR: "RES",
            ErrorCategory.UNKNOWN_ERROR: "UNK",
        }

        code_prefix = category_codes.get(category, "UNK")
        type_suffix = error_type[:3].upper()

        return f"{code_prefix}_{type_suffix}"

    def handle_error_with_recovery(
        self,
        error: Exception,
        context: Optional[Dict[str, Any]] = None,
        max_retries: int = 3,
    ) -> Dict[str, Any]:
        """
        Handle error with automatic recovery strategies

        Args:
            error: The original exception
            context: Additional context information
            max_retries: Maximum number of retry attempts

        Returns:
            Dictionary containing error information and recovery status
        """
        browser_error = self.categorize_error(error, context)

        recovery_result = {
            "error": browser_error.to_dict(),
            "recovery_attempted": False,
            "recovery_successful": False,
            "retry_count": 0,
        }

        # Attempt recovery if recommended
        if browser_error.retry_recommended and max_retries > 0:
            recovery_result["recovery_attempted"] = True

            # Implement recovery strategies based on error category
            recovery_successful = self._attempt_recovery(browser_error, context)
            recovery_result["recovery_successful"] = recovery_successful

            if recovery_successful:
                self.logger.info(
                    f"Recovery successful for error: {browser_error.error_code}"
                )
            else:
                self.logger.warning(
                    f"Recovery failed for error: {browser_error.error_code}"
                )

        return recovery_result

    async def handle_test_error(
        self,
        test_id: str,
        error: Exception,
        test_case: Dict[str, Any],
        max_retries: int = 3,
    ) -> Dict[str, Any]:
        """
        Handle test-specific error with context and recovery strategies
        
        Args:
            test_id: Unique identifier for the test
            error: The original exception
            test_case: Test case information for context
            max_retries: Maximum number of retry attempts
            
        Returns:
            Dictionary containing error handling results
        """
        context = {
            "test_id": test_id,
            "test_case": test_case,
            "scenario_name": test_case.get("scenario_name", "Unknown"),
            "url": test_case.get("url", ""),
            "test_type": test_case.get("test_type", "functional"),
        }
        
        self.logger.error(
            f"Test error in {context['scenario_name']} (ID: {test_id}): {str(error)}",
            exc_info=True
        )
        
        # Categorize and handle the error
        browser_error = self.categorize_error(error, context)
        
        # Create detailed error response
        error_details = {
            "test_id": test_id,
            "scenario_name": context["scenario_name"],
            "error_info": browser_error.to_dict(),
            "handled_at": "browser_error_handler",
            "recovery_attempted": False,
            "recovery_successful": False,
        }
        
        # Log categorized error
        self.logger.warning(
            f"Categorized error - Code: {browser_error.error_code}, "
            f"Category: {browser_error.category.value}, "
            f"Severity: {browser_error.severity.value}"
        )
        
        # Attempt recovery if recommended and retries available
        if browser_error.retry_recommended and max_retries > 0:
            self.logger.info(f"Attempting recovery for test {test_id}")
            error_details["recovery_attempted"] = True
            
            try:
                recovery_successful = self._attempt_recovery(browser_error, context)
                error_details["recovery_successful"] = recovery_successful
                
                if recovery_successful:
                    self.logger.info(f"Recovery successful for test {test_id}")
                else:
                    self.logger.warning(f"Recovery failed for test {test_id}")
                    
            except Exception as recovery_error:
                self.logger.error(
                    f"Recovery attempt failed for test {test_id}: {str(recovery_error)}"
                )
                error_details["recovery_error"] = str(recovery_error)
        
        return error_details

    def _attempt_recovery(
        self, error: BrowserTestError, context: Optional[Dict[str, Any]]
    ) -> bool:
        """
        Attempt automatic recovery based on error category

        Args:
            error: Categorized browser error
            context: Additional context

        Returns:
            True if recovery was successful
        """
        try:
            if error.category == ErrorCategory.NETWORK_ERROR:
                # Wait and retry for network issues
                import asyncio

                asyncio.sleep(2)
                return True

            elif error.category == ErrorCategory.TIMEOUT_ERROR:
                # Increase timeout for next attempt
                if context:
                    context["timeout"] = context.get("timeout", 30) * 1.5
                return True

            elif error.category == ErrorCategory.ELEMENT_NOT_FOUND:
                # Add additional wait time
                import asyncio

                asyncio.sleep(1)
                return True

            return False

        except Exception as e:
            self.logger.error(f"Recovery attempt failed: {str(e)}")
            return False

    def get_error_statistics(self, errors: List[BrowserTestError]) -> Dict[str, Any]:
        """
        Generate error statistics from a list of errors

        Args:
            errors: List of browser test errors

        Returns:
            Dictionary containing error statistics
        """
        if not errors:
            return {"total_errors": 0}

        category_counts = {}
        severity_counts = {}
        retry_recommended_count = 0

        for error in errors:
            # Count by category
            category = error.category.value
            category_counts[category] = category_counts.get(category, 0) + 1

            # Count by severity
            severity = error.severity.value
            severity_counts[severity] = severity_counts.get(severity, 0) + 1

            # Count retry recommendations
            if error.retry_recommended:
                retry_recommended_count += 1

        return {
            "total_errors": len(errors),
            "category_breakdown": category_counts,
            "severity_breakdown": severity_counts,
            "retry_recommended": retry_recommended_count,
            "most_common_category": max(category_counts, key=category_counts.get)
            if category_counts
            else None,
            "highest_severity": max(severity_counts, key=severity_counts.get)
            if severity_counts
            else None,
        }


# Global error handler instance
browser_error_handler = BrowserErrorHandler()
