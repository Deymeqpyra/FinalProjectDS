from datetime import date, datetime
from urllib.parse import urljoin
from playwright.async_api import async_playwright
from playwright_stealth import stealth_async
from bs4 import BeautifulSoup
from models import marketplace


async def scrape_product(marketplace: marketplace.Marketplace, product_name: str):
    search_url = marketplace.base_search_url.format(query=product_name)
    result = {
        "marketplace_id": marketplace.id,
        "product_title": None,
        "price": None,
        "url": None,
        "description": None,
        "scraped_at": date.today(),
        "status": "error_scraping",
        "error_message": None,
    }

    browser = None
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context()
            page = await context.new_page()

            await stealth_async(page)

            await page.goto(search_url, timeout=10000)
            await page.wait_for_timeout(6000)

            await page.wait_for_selector(marketplace.product_selector, timeout=10000)

            html = await page.content()

        soup = BeautifulSoup(html, "html.parser")

        title_element = soup.find(class_=marketplace.title_selector)
        price_element = soup.find(class_=marketplace.price_selector)
        url_element = soup.find(class_=marketplace.title_selector)
        desc_element = soup.find(class_=marketplace.description_selector)
        description = {}
        for dl in soup.find_all("dl"):
            dt = dl.find("dt")
            dd = dl.find("dd")
            if dt and dd:
                key = dt.get_text(strip=True)
                value = dd.get_text(strip=True)
                description[key] = value

        result["product_title"] = (
            title_element.get_text(strip=True) if title_element else None
        )
        result["price"] = price_element.get_text(strip=True) if price_element else None
        result["url"] = url_element.get("href") if url_element else None
        result["description"] = description if desc_element else None
        result["status"] = "success"

    except Exception as e:
        result["error_message"] = f"{type(e).__name__}: {str(e)}"
    finally:
        if browser:
            await browser.close()

    return result
