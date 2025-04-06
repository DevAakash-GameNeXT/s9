import asyncio
import csv
import os
from playwright.async_api import async_playwright

LIST = [
    'https://www.facebook.com/61559681968245/',
    'https://www.facebook.com/61559681968245/',
    'https://www.facebook.com/digitechelites/',
    'https://www.facebook.com/61572606607215/',
    'https://www.facebook.com/61572606607215/',
    'https://www.facebook.com/adoremyspace/',
    'https://www.facebook.com/61573698873277/',
    'https://www.facebook.com/61573032410206/',
    'https://www.facebook.com/61572615422820/',
    'https://www.facebook.com/61566381808367/',
]

phone_list = set()
chunk_size = 100
semaphore = asyncio.Semaphore(8)

# Load existing numbers from CSV to prevent duplicates
if os.path.exists("phones.csv"):
    with open("phones.csv", newline="") as f:
        reader = csv.reader(f)
        phone_list.update(row[0] for row in reader)

async def process_url(browser, url):
    async with semaphore:
        page = await browser.new_page()
        try:
            await page.goto(url)
            try:
                await page.click("div[aria-label='Close']", timeout=3000)
            except:
                pass
            await page.wait_for_selector("div[role='main']")
            await page.wait_for_timeout(3000)
            phone_element = page.locator("text=/\\+?[0-9][0-9\\-\\s]{8,}/").first
            if await phone_element.count() > 0:
                raw = await phone_element.inner_text()
                cleaned = raw.replace(" ", "")
                if cleaned not in phone_list:
                    phone_list.add(cleaned)
                    with open("phones.csv", "a", newline="") as f:
                        writer = csv.writer(f)
                        writer.writerow([cleaned])
        except:
            pass
        finally:
            await page.close()
            LIST.remove(url)

async def go():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        tasks = [process_url(browser, url) for url in LIST[:chunk_size]]
        await asyncio.gather(*tasks)
        await browser.close()

asyncio.run(go())
