from playwright.async_api import async_playwright
from datetime import datetime


async def scrape_product(marketplace, product_name):
    search_url = marketplace.base_search_url.format(query=product_name)
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
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
            await page.goto(search_url, timeout=20000)
            await page.wait_for_selector(marketplace.product_selector, timeout=10000)
            product_element = await page.query_selector(marketplace.product_selector)
            if not product_element:
                result["error_message"] = "Product element not found"
                return result
            title = await product_element.query_selector(marketplace.title_selector)
            price = await product_element.query_selector(marketplace.price_selector)
            link = await product_element.query_selector(marketplace.link_selector)
            result["product_title"] = await title.inner_text() if title else None
            result["price"] = await price.inner_text() if price else None
            result["url"] = await link.get_attribute("href") if link else None
            result["status"] = "success"
            result["error_message"] = None
            return result
        except Exception as e:
            result["error_message"] = str(e)
            return result
        finally:
            await browser.close()
