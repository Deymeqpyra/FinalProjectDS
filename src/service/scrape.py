from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import aiohttp
from datetime import datetime
from models import marketplace
from datetime import datetime
from playwright.async_api import async_playwright
from urllib.parse import urljoin


async def scrape_product(marketplace: marketplace.Marketplace, product_name: str):
    search_url = marketplace.base_search_url.format(query=product_name)
    result = {
        "marketplace_id": marketplace.id,
        "scraped_product_title": None,
        "scraped_price": None,
        "product_url": None,
        "scraped_at": datetime.now(),
        "status": "error_scraping",
        "error_message": None,
    }

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.set_extra_http_headers(
                {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                    "Accept-Language": "uk-UA,uk;q=0.9,en-US;q=0.8,en;q=0.7",
                }
            )
            await page.goto(search_url, timeout=20000)
            await page.mouse.move(100, 100)
            await page.mouse.click(100, 100)
            await page.wait_for_timeout(1500)

            await page.wait_for_selector(
                str(marketplace.product_selector), timeout=10000
            )

            product_element = await page.query_selector(
                str(marketplace.product_selector)
            )

            if not product_element:
                result["error_message"] = "Product element not found (even in iframe)"
                await browser.close()
                return result

            title_elem = await product_element.query_selector(
                str(marketplace.title_selector)
            )
            price_elem = await product_element.query_selector(
                str(marketplace.price_selector)
            )
            link_elem = await product_element.query_selector(
                str(marketplace.link_selector)
            )

            result["scraped_product_title"] = (
                await title_elem.inner_text() if title_elem else None
            )
            result["scraped_price"] = (
                await price_elem.inner_text() if price_elem else None
            )
            raw_href = await link_elem.get_attribute("href") if link_elem else None
            result["product_url"] = urljoin(search_url, raw_href) if raw_href else None
            result["status"] = "success"

            await browser.close()

    except Exception as e:
        result["error_message"] = str(e)

    return result
