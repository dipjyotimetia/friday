"""
Browser session management for improved performance and resource utilization.

This module manages browser sessions, contexts, and pages for efficient test execution.
"""

import asyncio
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from contextlib import asynccontextmanager
from dataclasses import dataclass, field

from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from friday.services.logger import get_logger

logger = get_logger(__name__)


@dataclass
class BrowserSession:
    """Represents a browser session with its context and metadata"""

    session_id: str
    browser: Browser
    context: BrowserContext
    page: Page
    created_at: datetime = field(default_factory=datetime.now)
    last_used: datetime = field(default_factory=datetime.now)
    is_active: bool = True
    test_count: int = 0
    browser_type: str = "chromium"
    headless: bool = True

    def update_last_used(self):
        """Update the last used timestamp"""
        self.last_used = datetime.now()
        self.test_count += 1


class BrowserSessionManager:
    """Manages browser sessions for efficient test execution"""

    def __init__(self, max_sessions: int = 5, session_timeout: int = 300):
        self.max_sessions = max_sessions
        self.session_timeout = session_timeout  # seconds
        self.sessions: Dict[str, BrowserSession] = {}
        self.playwright = None
        self.browsers: Dict[str, Browser] = {}
        self.logger = logger
        self._cleanup_task = None

    async def initialize(self):
        """Initialize the browser session manager"""
        try:
            self.playwright = await async_playwright().start()
            self.logger.info("Browser session manager initialized")

            # Start cleanup task
            self._cleanup_task = asyncio.create_task(self._cleanup_expired_sessions())
        except Exception as e:
            self.logger.error(f"Failed to initialize browser session manager: {str(e)}")
            raise

    async def shutdown(self):
        """Shutdown the browser session manager"""
        try:
            # Cancel cleanup task
            if self._cleanup_task:
                self._cleanup_task.cancel()

            # Close all sessions
            for session in list(self.sessions.values()):
                await self._close_session(session.session_id)

            # Close all browsers
            for browser in self.browsers.values():
                await browser.close()

            # Stop playwright
            if self.playwright:
                await self.playwright.stop()

            self.logger.info("Browser session manager shutdown completed")
        except Exception as e:
            self.logger.error(f"Error during shutdown: {str(e)}")

    async def get_or_create_session(
        self,
        browser_type: str = "chromium",
        headless: bool = True,
        viewport: Optional[Dict[str, int]] = None,
        user_agent: Optional[str] = None,
        extra_context_options: Optional[Dict[str, Any]] = None,
    ) -> BrowserSession:
        """
        Get an existing session or create a new one

        Args:
            browser_type: Type of browser (chromium, firefox, webkit)
            headless: Whether to run in headless mode
            viewport: Viewport dimensions
            user_agent: Custom user agent
            extra_context_options: Additional context options

        Returns:
            BrowserSession instance
        """
        try:
            # Try to find an available session with matching parameters
            available_session = self._find_available_session(browser_type, headless)
            if available_session:
                available_session.update_last_used()
                self.logger.info(
                    f"Reusing browser session: {available_session.session_id}"
                )
                return available_session

            # Create new session if none available and under limit
            if len(self.sessions) < self.max_sessions:
                return await self._create_new_session(
                    browser_type, headless, viewport, user_agent, extra_context_options
                )

            # Clean up expired sessions and try again
            await self._cleanup_expired_sessions()
            if len(self.sessions) < self.max_sessions:
                return await self._create_new_session(
                    browser_type, headless, viewport, user_agent, extra_context_options
                )

            # Force close oldest session if at limit
            oldest_session = min(self.sessions.values(), key=lambda s: s.last_used)
            await self._close_session(oldest_session.session_id)

            return await self._create_new_session(
                browser_type, headless, viewport, user_agent, extra_context_options
            )

        except Exception as e:
            self.logger.error(f"Failed to get or create browser session: {str(e)}")
            raise

    async def _create_new_session(
        self,
        browser_type: str,
        headless: bool,
        viewport: Optional[Dict[str, int]] = None,
        user_agent: Optional[str] = None,
        extra_context_options: Optional[Dict[str, Any]] = None,
    ) -> BrowserSession:
        """Create a new browser session"""
        try:
            session_id = str(uuid.uuid4())

            # Get or create browser
            browser = await self._get_or_create_browser(browser_type, headless)

            # Prepare context options
            context_options = {
                "viewport": viewport or {"width": 1920, "height": 1080},
                "user_agent": user_agent,
                "ignore_https_errors": True,
                "accept_downloads": True,
            }

            if extra_context_options:
                context_options.update(extra_context_options)

            # Filter out None values
            context_options = {
                k: v for k, v in context_options.items() if v is not None
            }

            # Create new context and page
            context = await browser.new_context(**context_options)
            page = await context.new_page()

            # Create session object
            session = BrowserSession(
                session_id=session_id,
                browser=browser,
                context=context,
                page=page,
                browser_type=browser_type,
                headless=headless,
            )

            self.sessions[session_id] = session
            self.logger.info(f"Created new browser session: {session_id}")
            return session

        except Exception as e:
            self.logger.error(f"Failed to create new browser session: {str(e)}")
            raise

    async def _get_or_create_browser(
        self, browser_type: str, headless: bool
    ) -> Browser:
        """Get or create a browser instance"""
        browser_key = f"{browser_type}_{headless}"

        if browser_key not in self.browsers:
            browser_launch_options = {
                "headless": headless,
                "args": [
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-web-security",
                    "--disable-features=VizDisplayCompositor",
                    "--disable-gpu",
                    "--disable-extensions",
                    "--no-first-run",
                ],
            }
            
            # Add additional args for headless mode to ensure compatibility
            if headless:
                browser_launch_options["args"].extend([
                    "--disable-background-timer-throttling",
                    "--disable-backgrounding-occluded-windows",
                    "--disable-renderer-backgrounding",
                ])

            if browser_type == "chromium":
                browser = await self.playwright.chromium.launch(
                    **browser_launch_options
                )
            elif browser_type == "firefox":
                browser = await self.playwright.firefox.launch(**browser_launch_options)
            elif browser_type == "webkit":
                browser = await self.playwright.webkit.launch(**browser_launch_options)
            else:
                raise ValueError(f"Unsupported browser type: {browser_type}")

            self.browsers[browser_key] = browser
            self.logger.info(f"Created new {browser_type} browser instance")

        return self.browsers[browser_key]

    def _find_available_session(
        self, browser_type: str, headless: bool
    ) -> Optional[BrowserSession]:
        """Find an available session matching the criteria"""
        for session in self.sessions.values():
            if (
                session.browser_type == browser_type
                and session.headless == headless
                and session.is_active
            ):
                return session
        return None

    async def release_session(self, session_id: str):
        """Release a session back to the pool"""
        if session_id in self.sessions:
            session = self.sessions[session_id]
            session.update_last_used()
            session.is_active = True
            self.logger.info(f"Released browser session: {session_id}")

    async def _close_session(self, session_id: str):
        """Close a specific session"""
        if session_id in self.sessions:
            try:
                session = self.sessions[session_id]
                await session.context.close()
                del self.sessions[session_id]
                self.logger.info(f"Closed browser session: {session_id}")
            except Exception as e:
                self.logger.error(f"Error closing session {session_id}: {str(e)}")

    async def _cleanup_expired_sessions(self):
        """Cleanup expired sessions periodically"""
        while True:
            try:
                current_time = datetime.now()
                expired_sessions = []

                for session_id, session in self.sessions.items():
                    time_since_last_used = current_time - session.last_used
                    if time_since_last_used > timedelta(seconds=self.session_timeout):
                        expired_sessions.append(session_id)

                for session_id in expired_sessions:
                    await self._close_session(session_id)
                    self.logger.info(f"Cleaned up expired session: {session_id}")

                await asyncio.sleep(60)  # Check every minute

            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in cleanup task: {str(e)}")
                await asyncio.sleep(60)

    @asynccontextmanager
    async def get_session_context(self, **kwargs):
        """Context manager for session usage"""
        session = await self.get_or_create_session(**kwargs)
        try:
            yield session
        finally:
            await self.release_session(session.session_id)

    def get_session_stats(self) -> Dict[str, Any]:
        """Get session statistics"""
        active_sessions = sum(1 for s in self.sessions.values() if s.is_active)
        total_tests = sum(s.test_count for s in self.sessions.values())

        browser_types = {}
        for session in self.sessions.values():
            browser_type = session.browser_type
            browser_types[browser_type] = browser_types.get(browser_type, 0) + 1

        return {
            "total_sessions": len(self.sessions),
            "active_sessions": active_sessions,
            "max_sessions": self.max_sessions,
            "total_tests_executed": total_tests,
            "browser_types": browser_types,
            "session_timeout": self.session_timeout,
        }

    async def take_screenshot(self, session_id: str, full_page: bool = True) -> bytes:
        """Take a screenshot using the specified session"""
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")

        session = self.sessions[session_id]
        return await session.page.screenshot(full_page=full_page)

    async def execute_script(self, session_id: str, script: str) -> Any:
        """Execute JavaScript in the specified session"""
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")

        session = self.sessions[session_id]
        return await session.page.evaluate(script)

    async def create_browser_context(
        self,
        test_id: str,
        headless: bool = True,
        browser_type: str = "chromium",
        viewport: Optional[Dict[str, int]] = None,
        **context_options
    ) -> BrowserContext:
        """
        Create a new browser context for a specific test
        
        Args:
            test_id: Unique identifier for the test
            headless: Whether to run in headless mode
            browser_type: Type of browser to use
            viewport: Viewport dimensions
            **context_options: Additional context options
            
        Returns:
            BrowserContext instance
        """
        try:
            self.logger.info(f"Creating browser context for test: {test_id}")
            
            # Get or create browser
            browser = await self._get_or_create_browser(browser_type, headless)
            
            # Prepare context options
            default_options = {
                "viewport": viewport or {"width": 1920, "height": 1080},
                "ignore_https_errors": True,
                "accept_downloads": True,
                "record_video_dir": f"test_videos/{test_id}" if not headless else None,
                "record_har_path": f"test_hars/{test_id}.har",
            }
            
            # Merge with additional options
            final_options = {**default_options, **context_options}
            
            # Filter out None values
            final_options = {
                k: v for k, v in final_options.items() if v is not None
            }
            
            # Create new context
            context = await browser.new_context(**final_options)
            
            # Set up context event handlers for better error handling
            context.on("page", lambda page: self._setup_page_handlers(page, test_id))
            
            self.logger.info(f"Successfully created browser context for test: {test_id}")
            return context
            
        except Exception as e:
            self.logger.error(f"Failed to create browser context for test {test_id}: {str(e)}")
            raise

    def _setup_page_handlers(self, page: Page, test_id: str):
        """Set up event handlers for a new page"""
        try:
            # Handle console messages
            page.on("console", lambda msg: self.logger.debug(
                f"Test {test_id} console [{msg.type}]: {msg.text}"
            ))
            
            # Handle page errors
            page.on("pageerror", lambda error: self.logger.error(
                f"Test {test_id} page error: {str(error)}"
            ))
            
            # Handle dialog events (alerts, confirms, etc.)
            page.on("dialog", lambda dialog: asyncio.create_task(
                self._handle_dialog(dialog, test_id)
            ))
            
        except Exception as e:
            self.logger.error(f"Failed to setup page handlers for test {test_id}: {str(e)}")

    async def _handle_dialog(self, dialog, test_id: str):
        """Handle browser dialogs (alerts, confirms, etc.)"""
        try:
            self.logger.info(
                f"Test {test_id} dialog [{dialog.type}]: {dialog.message}"
            )
            # Accept dialogs by default
            await dialog.accept()
        except Exception as e:
            self.logger.error(f"Failed to handle dialog for test {test_id}: {str(e)}")


# Global browser session manager instance
browser_session_manager = BrowserSessionManager()
