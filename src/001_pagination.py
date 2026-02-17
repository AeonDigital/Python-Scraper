import sys
import time
import csv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup

def scrape_all(domain, path, product_node_selector, product_name_selector, product_link_selector, next_selector, csv_filename):
    url = f"{domain}{path}"

    # Configure Chrome browser options
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run browser in headless mode (no GUI window)
    options.add_argument("--no-sandbox")  # Required in some Linux environments
    options.add_argument("--disable-dev-shm-usage")  # Prevents issues on systems with limited shared memory
    options.add_argument("--disable-blink-features=AutomationControlled")  # Avoid detection as automated browser
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                         "AppleWebKit/537.36 (KHTML, like Gecko) "
                         "Chrome/122.0 Safari/537.36")

    # Path to ChromeDriver executable
    service = Service("/usr/bin/chromedriver")
    driver = webdriver.Chrome(service=service, options=options)

    page_items = []
    page_num = 1

    while url:
        print(f"\n>>> Scraping page {page_num}: {url}")
        driver.get(url)
        time.sleep(3)  # wait for page to load

        soup = BeautifulSoup(driver.page_source, "html.parser")

        # Extract product nodes
        product_nodes = soup.select(product_node_selector)
        items = 0
        for el in product_nodes:
            node_name = el.select_one(product_name_selector)
            node_link = el.select_one(product_link_selector)

            name = node_name.get_text(strip=True).replace('"', "'")
            href = node_link.get("href")
            if href:
                if href.startswith("/"):
                    href = domain + href

                items = items + 1
                page_items.append((name, href))

        print(f"Items found on this page: {items}")

        # Look for next page link
        next_page = soup.select_one(next_selector)
        if next_page and next_page.get("href"):
            href = next_page.get("href")
            url = domain + href if href.startswith("/") else href
            page_num += 1
        else:
            url = None  # no next page available

    driver.quit()

    # Save results to CSV
    with open(csv_filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        writer.writerow(["Name", "Link"])
        for name, href in page_items:
            writer.writerow([name, href])

    return page_items


if __name__ == "__main__":
    if len(sys.argv) < 6:
        print("Usage: python 001_pagination.py <domain> <path> <product node selector> <product name selector> <product link selector> <next page selector> <csv file name.csv>")
        sys.exit(1)

    domain = sys.argv[1]
    path = sys.argv[2]
    product_node_selector = sys.argv[3]
    product_name_selector = sys.argv[4]
    product_link_selector = sys.argv[5]
    next_selector = sys.argv[6]
    csv_filename = sys.argv[7]

    items = scrape_all(domain, path, product_node_selector, product_name_selector, product_link_selector, next_selector, csv_filename)

    print("\n=== Final result ===")
    print(f"Total items found: {len(items)}\n")
    print(f"Data saved to: {csv_filename}")