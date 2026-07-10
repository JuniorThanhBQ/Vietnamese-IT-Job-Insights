import asyncio
import random
from typing import Optional
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from loguru import logger


# pylint: disable=too-many-instance-attributes
class BaseCrawler:
    """
    Base asynchronous crawler using Playwright.
    Implements memory and resource optimizations for low-spec hosts (8GB RAM limit):
    - Concurrency capped at 2 parallel tabs using an internal semaphore.
    - Asset blocking (images, fonts, media, and optionally stylesheets) to reduce bandwidth and CPU.
    - Random human-like delays and user-agent rotations to avoid detection.
    """

    def __init__(
        self,
        headless: bool = True,
        max_tabs: int = 2,
        block_assets: bool = True,
        timeout_ms: int = 30000
    ):
        self.headless = headless
        self.max_tabs = max_tabs
        self.block_assets = block_assets
        self.timeout_ms = timeout_ms

        self._playwright = None
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None
        self._semaphore = asyncio.Semaphore(max_tabs)

        # A list of modern user agents to rotate
        # pylint: disable=line-too-long
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/120.0",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ]

    async def start(self) -> None:
        """Initialize Playwright and launch the browser instance."""
        if self._browser:
            return

        logger.info("Initializing Playwright browser context...")
        self._playwright = await async_playwright().start()

        # Launch Chromium with memory-optimized flags
        self._browser = await self._playwright.chromium.launch(
            headless=self.headless,
            args=[
                "--disable-dev-shm-usage",
                "--no-sandbox",
                "--disable-gpu",
                "--js-flags=--max-old-space-size=512"  # Limit V8 heap memory size to save RAM
            ]
        )

        # Create context with a default viewport and random user agent
        self._context = await self._browser.new_context(
            user_agent=random.choice(self.user_agents),
            viewport={"width": 1280, "height": 800},
            bypass_csp=True
        )

        # Set default timeout for all actions
        self._context.set_default_timeout(self.timeout_ms)
        logger.info("Playwright browser initialized successfully.")

    async def _route_intercept(self, route) -> None:
        """Intercept network requests to block unnecessary asset downloads (images, fonts, media)."""
        resource_type = route.request.resource_type
        if resource_type in ("image", "font", "media"):
            await route.abort()
        elif self.block_assets and resource_type == "stylesheet":
            await route.abort()
        else:
            await route.continue_()

    async def get_page(self) -> Page:
        """Create a new page tab in the browser context with routing optimizations."""
        if not self._context:
            await self.start()

        page = await self._context.new_page()

        # Intercept and abort resource-heavy requests
        if self.block_assets:
            await page.route("**/*", self._route_intercept)

        return page

    async def fetch_page_html(
        self,
        url: str,
        wait_selector: Optional[str] = None,
        delay_range: tuple[float, float] = (1.0, 3.0)
    ) -> str:
        """
        Navigates to a URL and returns its HTML content.
        Uses an internal semaphore to enforce the 2-tab limit.
        """
        async with self._semaphore:
            # Random delay before request to mimic human browsing behavior
            delay = random.uniform(*delay_range)
            await asyncio.sleep(delay)

            page = await self.get_page()
            try:
                logger.info(f"Navigating to: {url}")
                await page.goto(url, wait_until="domcontentloaded")

                if wait_selector:
                    await page.wait_for_selector(wait_selector, timeout=self.timeout_ms)

                # Fetch and return the page HTML
                html = await page.content()
                return html
            except Exception as e:
                logger.error(f"Error fetching page {url}: {str(e)}")
                raise e
            finally:
                # Always close the page tab to free memory
                await page.close()

    async def close(self) -> None:
        """Shutdown the browser and Playwright instances, releasing resources."""
        logger.info("Closing Playwright browser context...")
        if self._context:
            await self._context.close()
            self._context = None
        if self._browser:
            await self._browser.close()
            self._browser = None
        if self._playwright:
            await self._playwright.stop()
            self._playwright = None
        logger.info("Playwright browser context closed.")

    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
