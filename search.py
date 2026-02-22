"""Product search via Playwright headless Chromium.

Searches Google Shopping / DuckDuckGo for product info.
Copied and adapted from Mike's relay/browser.py.
"""

import logging
import re

logger = logging.getLogger(__name__)


def _clean_text(text: str, max_chars: int = 4000) -> str:
    """Strip excessive whitespace and truncate."""
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r" {2,}", " ", text)
    text = text.strip()
    if len(text) > max_chars:
        text = text[:max_chars] + f"\n\n[Truncated — {len(text)} chars total]"
    return text


def search_product(query: str, timeout: int = 15000) -> dict:
    """Search DuckDuckGo for product info. Returns text summary."""
    try:
        from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

        search_url = f"https://duckduckgo.com/?q={query.replace(' ', '+')}&ia=shopping"

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            try:
                ctx = browser.new_context(
                    user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36"
                )
                page = ctx.new_page()
                page.goto(search_url, wait_until="domcontentloaded", timeout=timeout)
                page.wait_for_timeout(2000)  # let JS render results
                title = page.title()
                content = page.inner_text("body")
                return {
                    "success": True,
                    "query": query,
                    "title": title,
                    "content": _clean_text(content),
                }
            except PWTimeout:
                return {"success": False, "error": f"Timeout searching for '{query}'"}
            finally:
                browser.close()

    except Exception as e:
        logger.error(f"search_product failed: {e}")
        return {"success": False, "error": str(e)}
