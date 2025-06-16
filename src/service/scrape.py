from datetime import datetime
from urllib.parse import urljoin
from playwright.async_api import async_playwright
from playwright_stealth import stealth_async
from bs4 import BeautifulSoup
from models import marketplace


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

    browser = None
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()

            await stealth_async(page)

            await page.goto(search_url, timeout=30000)
            await page.wait_for_timeout(6000)  # час на рендеринг

            # Очікуємо, поки елемент з селектором Playwright стане видимим
            await page.wait_for_selector(marketplace.product_selector, timeout=10000)

            html = await page.content()

        # Парсимо отриманий HTML через BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")

        product_element = soup.select_one(marketplace.product_selector)
        if not product_element:
            result["error_message"] = "Product element not found in BeautifulSoup"
            return result

        title_elem = product_element.select_one(marketplace.title_selector)
        price_elem = product_element.select_one(marketplace.price_selector)
        link_elem = product_element.select_one(marketplace.link_selector)

        result["scraped_product_title"] = (
            title_elem.get_text(strip=True) if title_elem else None
        )
        result["scraped_price"] = (
            price_elem.get_text(strip=True) if price_elem else None
        )

        raw_href = link_elem.get("href") if link_elem else None
        result["product_url"] = urljoin(search_url, raw_href) if raw_href else None
        result["status"] = "success"

    except Exception as e:
        result["error_message"] = f"{type(e).__name__}: {str(e)}"
    finally:
        if browser:
            await browser.close()

    return result
