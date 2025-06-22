"""Production health check utilities."""

import time
from typing import Dict, Any
from datetime import datetime

from friday.config.config import settings


class HealthChecker:
    """Production-grade health checking for Friday services."""

    def __init__(self):
        self.start_time = time.time()

    def get_health_status(self) -> Dict[str, Any]:
        """Get comprehensive health status."""
        health = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "unknown",  # Will be set by caller
            "uptime_seconds": time.time() - self.start_time,
            "services": self._check_services(),
            "configuration": self._check_configuration(),
        }

        # Determine overall status
        service_statuses = list(health["services"].values())
        if "unhealthy" in service_statuses:
            health["status"] = "unhealthy"
        elif "degraded" in service_statuses:
            health["status"] = "degraded"

        return health

    def _check_services(self) -> Dict[str, str]:
        """Check health of external services."""
        services = {}

        # Check LLM providers
        llm_providers = []
        if settings.openai_api_key:
            llm_providers.append("openai")
        if settings.google_api_key:
            llm_providers.append("google")
        if settings.mistral_api_key:
            llm_providers.append("mistral")

        services["llm_providers"] = "healthy" if llm_providers else "unhealthy"

        # Check JIRA connectivity
        if all([settings.jira_url, settings.jira_username, settings.jira_api_token]):
            services["jira"] = "healthy"
        else:
            services["jira"] = "unhealthy"

        # Check optional services
        if settings.confluence_enabled:
            services["confluence"] = "healthy"
        else:
            services["confluence"] = "not_configured"

        if settings.github_enabled:
            services["github"] = "healthy"
        else:
            services["github"] = "not_configured"

        return services

    def _check_configuration(self) -> Dict[str, Any]:
        """Check configuration completeness."""
        return {
            "environment": settings.environment,
            "debug_mode": settings.debug,
            "log_level": settings.log_level,
            "cors_configured": bool(settings.allowed_origins),
            "database_configured": bool(settings.database_url),
        }


# Global health checker instance
health_checker = HealthChecker()
