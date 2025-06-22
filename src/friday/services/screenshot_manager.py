"""
Screenshot management service for browser testing.

This module handles screenshot capture, storage, and retrieval for browser test results.
"""

import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import base64
import json

from friday.services.logger import get_logger

logger = get_logger(__name__)


class ScreenshotManager:
    """Manages screenshots for browser test execution"""

    def __init__(self, base_path: str = "screenshots"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(exist_ok=True)
        self.logger = logger

    def create_test_directory(self, test_id: str) -> Path:
        """
        Create a directory for a specific test execution

        Args:
            test_id: Unique identifier for the test

        Returns:
            Path to the created directory
        """
        test_dir = self.base_path / test_id
        test_dir.mkdir(exist_ok=True)
        self.logger.info(f"Created screenshot directory: {test_dir}")
        return test_dir

    def save_screenshot(
        self,
        test_id: str,
        screenshot_data: bytes,
        step_name: str = "screenshot",
        format: str = "png",
    ) -> str:
        """
        Save a screenshot to disk

        Args:
            test_id: Unique identifier for the test
            screenshot_data: Screenshot data as bytes
            step_name: Name of the test step
            format: Image format (png, jpg)

        Returns:
            Path to the saved screenshot
        """
        try:
            test_dir = self.create_test_directory(test_id)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
            filename = f"{step_name}_{timestamp}.{format}"
            screenshot_path = test_dir / filename

            with open(screenshot_path, "wb") as f:
                f.write(screenshot_data)

            relative_path = str(screenshot_path.relative_to(self.base_path))
            self.logger.info(f"Screenshot saved: {relative_path}")
            return relative_path
        except Exception as e:
            self.logger.error(f"Failed to save screenshot: {str(e)}")
            raise

    def save_base64_screenshot(
        self, test_id: str, base64_data: str, step_name: str = "screenshot"
    ) -> str:
        """
        Save a base64 encoded screenshot

        Args:
            test_id: Unique identifier for the test
            base64_data: Base64 encoded screenshot data
            step_name: Name of the test step

        Returns:
            Path to the saved screenshot
        """
        try:
            # Remove data URL prefix if present
            if base64_data.startswith("data:image"):
                base64_data = base64_data.split(",")[1]

            screenshot_bytes = base64.b64decode(base64_data)
            return self.save_screenshot(test_id, screenshot_bytes, step_name)
        except Exception as e:
            self.logger.error(f"Failed to save base64 screenshot: {str(e)}")
            raise

    def get_test_screenshots(self, test_id: str) -> List[Dict[str, Any]]:
        """
        Get all screenshots for a test

        Args:
            test_id: Unique identifier for the test

        Returns:
            List of screenshot metadata
        """
        try:
            test_dir = self.base_path / test_id
            if not test_dir.exists():
                return []

            screenshots = []
            for screenshot_file in test_dir.glob("*.png"):
                stat = screenshot_file.stat()
                screenshots.append(
                    {
                        "filename": screenshot_file.name,
                        "path": str(screenshot_file.relative_to(self.base_path)),
                        "size": stat.st_size,
                        "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                        "url": f"/api/v1/browser-test/screenshots/{test_id}/{screenshot_file.name}",
                    }
                )

            # Sort by creation time
            screenshots.sort(key=lambda x: x["created_at"])
            return screenshots
        except Exception as e:
            self.logger.error(f"Failed to get test screenshots: {str(e)}")
            return []

    def get_screenshot_path(self, test_id: str, filename: str) -> Optional[Path]:
        """
        Get the full path to a specific screenshot

        Args:
            test_id: Test identifier
            filename: Screenshot filename

        Returns:
            Path to the screenshot file or None if not found
        """
        screenshot_path = self.base_path / test_id / filename
        return screenshot_path if screenshot_path.exists() else None

    def cleanup_test_screenshots(self, test_id: str) -> bool:
        """
        Clean up screenshots for a specific test

        Args:
            test_id: Test identifier

        Returns:
            True if cleanup was successful
        """
        try:
            test_dir = self.base_path / test_id
            if test_dir.exists():
                for file in test_dir.glob("*"):
                    file.unlink()
                test_dir.rmdir()
                self.logger.info(f"Cleaned up screenshots for test: {test_id}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to cleanup screenshots: {str(e)}")
            return False

    def save_test_metadata(self, test_id: str, metadata: Dict[str, Any]) -> None:
        """
        Save test metadata alongside screenshots

        Args:
            test_id: Test identifier
            metadata: Test metadata to save
        """
        try:
            test_dir = self.create_test_directory(test_id)
            metadata_path = test_dir / "metadata.json"

            with open(metadata_path, "w") as f:
                json.dump(metadata, f, indent=2, default=str)

            self.logger.info(f"Test metadata saved for: {test_id}")
        except Exception as e:
            self.logger.error(f"Failed to save test metadata: {str(e)}")

    def get_test_metadata(self, test_id: str) -> Optional[Dict[str, Any]]:
        """
        Get test metadata

        Args:
            test_id: Test identifier

        Returns:
            Test metadata or None if not found
        """
        try:
            metadata_path = self.base_path / test_id / "metadata.json"
            if metadata_path.exists():
                with open(metadata_path, "r") as f:
                    return json.load(f)
            return None
        except Exception as e:
            self.logger.error(f"Failed to get test metadata: {str(e)}")
            return None

    def generate_test_id(self) -> str:
        """
        Generate a unique test ID

        Returns:
            Unique test identifier
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        return f"{timestamp}_{unique_id}"

    def get_storage_stats(self) -> Dict[str, Any]:
        """
        Get storage statistics

        Returns:
            Storage statistics
        """
        try:
            total_size = 0
            total_files = 0
            test_count = 0

            for test_dir in self.base_path.iterdir():
                if test_dir.is_dir():
                    test_count += 1
                    for file in test_dir.rglob("*"):
                        if file.is_file():
                            total_files += 1
                            total_size += file.stat().st_size

            return {
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "total_files": total_files,
                "test_count": test_count,
                "base_path": str(self.base_path),
            }
        except Exception as e:
            self.logger.error(f"Failed to get storage stats: {str(e)}")
            return {}

    async def capture_screenshot(
        self,
        context,
        test_id: str,
        step_name: str = "screenshot",
        full_page: bool = True,
    ) -> Optional[Path]:
        """
        Capture a screenshot from a browser context
        
        Args:
            context: Browser context or page to capture from
            test_id: Unique identifier for the test
            step_name: Name for this screenshot step
            full_page: Whether to capture the full page
            
        Returns:
            Path to the saved screenshot or None if failed
        """
        try:
            # Create test directory
            test_dir = self.create_test_directory(test_id)
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%H%M%S")
            filename = f"{step_name}_{timestamp}.png"
            screenshot_path = test_dir / filename
            
            # Capture screenshot from context or page
            if hasattr(context, 'pages') and context.pages:
                # It's a browser context, get the first page
                page = context.pages[0]
            elif hasattr(context, 'screenshot'):
                # It's a page
                page = context
            else:
                self.logger.error(f"Invalid context type for screenshot capture: {type(context)}")
                return None
                
            # Take the screenshot
            screenshot_bytes = await page.screenshot(
                path=screenshot_path,
                full_page=full_page
            )
            
            self.logger.info(f"Screenshot captured: {screenshot_path}")
            return screenshot_path
            
        except Exception as e:
            self.logger.error(f"Failed to capture screenshot for {test_id}: {str(e)}")
            return None


# Global screenshot manager instance
screenshot_manager = ScreenshotManager()
